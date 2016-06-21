from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone


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

    def get_absolute_url(self):
        return reverse('photo', kwargs={'photo_id': self.pk})


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name='Тег')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_id': self.pk})


class PhotoTags(models.Model):
    photo = models.ForeignKey(Photo, verbose_name='Фото')
    tag = models.ForeignKey(Tag, verbose_name='Тег')

    class Meta:
        verbose_name = 'Облако тегов'
        verbose_name_plural = 'Облако тегов'

    def __str__(self):
        return 'Метка фотографии №%s' % self.photo_id


class Like(models.Model):
    photo = models.ForeignKey(Photo, verbose_name='Фото')
    user = models.ForeignKey(User, verbose_name='Пользователь')
    rating = models.SmallIntegerField(default=0, blank=True, verbose_name='Оценка')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return 'Лайк пользователя №%s' % self.pk

    def save(self, *args, **kwargs):
        if self.rating:
            if self.rating > 1:
                self.rating = 1
            elif self.rating < -1:
                self.rating = -1

        super(Like, self).save(*args, **kwargs)