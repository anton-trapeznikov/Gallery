from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from urllib.parse import urlencode


class Photo(models.Model):
    src = models.URLField(verbose_name='URL фото')
    created_at = models.DateTimeField(default=timezone.now, blank=True, db_index=True, verbose_name='Создан')
    owner = models.ForeignKey(User, verbose_name='Владелец')
    rating = models.IntegerField(default=0, blank=True, db_index=True,verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def __str__(self):
        return 'Фото №%s' % self.pk

    @staticmethod
    @transaction.atomic
    def prepare(photo_ids=[]):
        '''
        Расчитывает рейтинг фотографий с блокировкой записи.
        TODO: проверить, что mysql поддерживает SELECT FOR UPDATE

        '''

        data = Photo.objects.filter(pk__in=photo_ids) \
            .annotate(like_rating=Sum('likes__rating')) \
            .values('pk', 'like_rating')

        for result in data:
            Photo.objects.select_for_update() \
                .filter(pk=result['pk']) \
                .update(rating=result['like_rating'] or 0)


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name='Тег')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('homepage') + '?' + urlencode({'tag': self.pk})


class PhotoTags(models.Model):
    photo = models.ForeignKey(Photo, verbose_name='Фото', related_name='tags')
    tag = models.ForeignKey(Tag, verbose_name='Тег')

    class Meta:
        verbose_name = 'Облако тегов'
        verbose_name_plural = 'Облако тегов'

    def __str__(self):
        return 'Метка фотографии №%s' % self.photo_id


class Like(models.Model):
    photo = models.ForeignKey(Photo, verbose_name='Фото', related_name='likes')
    user = models.ForeignKey(User, verbose_name='Пользователь')
    rating = models.IntegerField(default=0, blank=True, verbose_name='Оценка')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ('photo', 'user')

    def __str__(self):
        return 'Лайк пользователя №%s' % self.pk

    def __init__(self, *args, **kwargs):
        super(Like, self).__init__(*args, **kwargs)
        self._original_photo_id = self.photo_id

    def save(self, *args, **kwargs):
        if self.rating:
            if self.rating > 1:
                self.rating = 1
            elif self.rating < -1:
                self.rating = -1

        super(Like, self).save(*args, **kwargs)