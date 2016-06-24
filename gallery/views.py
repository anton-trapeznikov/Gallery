from django.db.models import Sum
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
#from django.views.generic.edit import FormMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from gallery.models import Photo, PhotoTags, Like
from gallery.forms import FilterForm
import json


class PhotoListView(ListView):
    model = Photo
    context_object_name = 'photos'
    paginate_by = 20

    def get_queryset(self):

        # Возможные сортировки набора данных.
        ordering = {
            'date-desc': ['-created_at',],
            'date-asc': ['created_at',],
            'rating-desc': ['-rating',],
            'rating-asc': ['rating',],
        }

        # Выбранная сортировка набора данных
        order_by = ordering['date-desc']

        # Инициализация формы-фильтра
        self._form = FilterForm(self.request.GET.copy())

        photos = Photo.objects.all()

        # Применение фильтра
        if self._form.is_valid():
            for param, value in self._form.cleaned_data.items():
                if value:
                    # Фильтрация по пересечению тегов
                    if param == 'tag':
                        for tag_id in [int(v) for v in value]:
                            photos = photos.filter(tags__tag_id=tag_id)

                    # Исключение фотографий содержащих любой из выбранных
                    # Исключающих тегов
                    elif param == 'ex_tag':
                        ex_tag_id = [int(v) for v in value]
                        photos = photos.exclude(tags__tag_id__in=ex_tag_id)

                    # Выбор сортировки
                    elif param == 'order':
                        if value in list(ordering.keys()):
                            order_by = ordering[value]

        # Применение сортировки
        return photos.select_related('owner').order_by(*order_by)
        #return photos.select_related('owner').annotate(like_rating=Sum('likes__rating')).order_by('-like_rating')

    def get_context_data(self, **kwargs):
        context = super(PhotoListView, self).get_context_data(**kwargs)
        context['form'] = self._form

        # Извлечение кверисета photos и извлечение тегов конкретных фотографий.
        photos = context['photos']

        # Индексный словарь тегов, формируемый одним запросом.
        # Ключом словаря является pk фотографии, значение -- список тегов.
        tags = {}

        photo_ids = [p.pk for p in photos]
        for tag in PhotoTags.objects.filter(photo_id__in=photo_ids).select_related('tag'):
            if tag.photo_id not in tags.keys():
                tags[tag.photo_id] = []

            tags[tag.photo_id].append(tag.tag)

        # Каждому экземпляру кверисета photos присваевается поле photo_tags,
        # содержащее список тегов данного экземпляра
        for photo in photos:
            if photo.pk in tags.keys():
                photo.photo_tag = tags[photo.pk]
            else:
                photo.photo_tag = []

        return context


@login_required
def set_like(request, pid, val):
    if request.is_ajax():
        '''
        Установка лайка пользователем.
        В случае успеха возвращает общий рейтинг лайкнутой фотографии.
        В случае неуспеха - None.

        '''

        # Возвращаемое значение
        response = None

        try:
            pid = int(pid)
            val = int(val)
        except (ValueError, TypeError):
            pass
        else:
            # Проверка существования фото с pk = pid
            if Photo.objects.filter(id=pid).count() > 0:

                # Если пользователь уже лайкал эту фотографию, то получаем
                # экземпляр модели Like. В противном случае создаем его.
                # Аналог get_or_create, но для created == True
                # экономится сейв.

                try:
                    like = Like.objects.get(photo_id=pid, user=request.user)
                except ObjectDoesNotExist:
                    like = Like(photo_id=pid, user=request.user)

                like.rating = like.rating + val if like.rating else val
                like.save()

                # Расчет общего рейтинга лайкнутой фотографии
                rating = like.photo.likes.aggregate(Sum('rating'))
                response = rating['rating__sum']

        return HttpResponse(json.dumps(response))

    raise Http404




