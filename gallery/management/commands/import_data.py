from django.db.models.signals import post_save, pre_delete, post_delete
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.contrib.auth.models import User
from django.db import transaction
from django.db import connection
from django.db.models import Sum
from django.conf import settings
from gallery.models import *
import random
import uuid
import time
import csv
import os


class Importer(object):
    '''
    Класс парсит и выгружает информацию о фотографиях из csv-файла,
    находящегося в BASE_DIR/test_data/.

    Единственный публичный метод - import_data().

    '''

    def __init__(self):
        self._url_validator = URLValidator()

        # Чтение csv-файла. Результат хранится в _data.
        data_file = os.path.join(settings.BASE_DIR, 'test_data', 'test-photo.csv')
        self._data = []
        if os.path.exists(data_file) and os.path.isfile(data_file):
            with open(data_file, 'r') as f:
                self._data = list(csv.reader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL))

        # Словарь для быстрого сопоставления внешнего и внутреннего
        # id пользователя, где ключ - id в csv, а значение - pk экземпляра модели.
        self._user_index = {}

        # Список ID выгруженных фото.
        self._photo_ids = []

        # Количество итераций загрузки данных из файла.
        self._multiplier = 10

        # Отключение сигналов
        post_save.disconnect(sender='Like', dispatch_uid='like-post-save')
        pre_delete.disconnect(sender='Like', dispatch_uid='like-pre-delete')
        post_delete.disconnect(sender='Like', dispatch_uid='like-post-delete')

    def import_data(self):
        if self._data:
            # Очистка БД
            self._clear_db()

            # Выгрузка пользователей
            self._import_users()

            # Заполнение self._user_index
            self._build_user_index()

            # Выгрузка фотографий
            self._import_photo()

            # Заполнение self._photo_ids
            self._build_photo_ids()

            # Генерация тегов
            self._build_tags()

            # Тегирование фотографий
            self._tag_photo()

            # Генерация лайков
            self._build_likes()

            # Расчет рейтингов (сумма лайков и дизлайков) фотографий
            self._calc_rating()

    def _clear_db(self):
        '''
        Очистка таблиц моделей от существующих записей.
        Удаляются также пользователи не обладающие статусом персонала.

        '''

        cursor = connection.cursor()
        models = (Like, PhotoTags, Tag, Photo)
        for model in models:
            cursor.execute('DELETE FROM `%s` WHERE 1' % model._meta.db_table)

        User.objects.all().exclude(is_staff=True).delete()


    @transaction.atomic
    def _import_users(self):
        '''
        Импорт пользователей и генерация имен вида
        u<внешний ID пользователя>.

        '''

        external_user_ids = set([r[0] for r in self._data])

        users = []
        for id in external_user_ids:
            user = User(username='u%s' % id)
            user.set_password(uuid.uuid4().hex[:8])
            users.append(user)

        User.objects.bulk_create(users, 2000)

    def _build_user_index(self):
        '''
        Метод генерирует cловарь self._user_index, предназначенный для
        сопоставления внешнего и внутреннего id пользователя, где
        ключ - id в csv,а значение - pk экземпляра модели.

        '''
        users = User.objects.all().only('pk', 'username')
        self._user_index = {u.username[1:]: u.pk for u in users}

    def _import_photo(self):
        '''
        Выгрузка всех фотографий с валидными урлами.
        Т.к. количество записей в csv (10^5) меньше необходимого (10^6),
        то выгрузка производится self._multiplier раз.

        Если self._multiplier == 1, то будет выгружено ~ 10^5 фотографий,
        если self._multiplier == 10, то будет выгружено ~ 10^6 фотографий.

        '''

        photos = []
        user_ids = self._user_index.keys()

        for multiplier in range(0, self._multiplier):
            for row in self._data:
                try:
                    self._url_validator(row[1])
                except ValidationError:
                    pass
                else:
                    p = Photo()
                    p.src = row[1]
                    p.owner_id = self._user_index[row[0]]
                    #p.created_at = time.mktime(time.strptime(row[2], '%Y-%m-%d %H:%M:%S'))
                    p.created_at = row[2]
                    photos.append(p)

        Photo.objects.bulk_create(photos, 2000)

    def _build_photo_ids(self):
        '''
        Метод генерирует список  self._photo_ids, содержащий
        pk всех имеющихся фотографий. Предназначен для
        повторного использования.

        '''

        self._photo_ids = [p.pk for p in Photo.objects.all().only('pk')]

    def _build_tags(self):
        '''
        Метод генерирует 100 тегов с именами вида T-[1-100].

        '''

        tags = [Tag(name='T-%s' % tag_no) for tag_no in range(1, 101)]
        Tag.objects.bulk_create(tags, 2000)

    def _tag_photo(self):
        '''
        Метод тегирует каждую из фотографий примерно пятью случайными тегами.
        '''

        tag_ids = [t.pk for t in Tag.objects.all().only('pk')]
        entries = []

        for pid in self._photo_ids:
            # Количество тегов
            tag_quantity = round(random.normalvariate(5, 1))

            if tag_quantity > 0:
                for tid in random.sample(tag_ids, tag_quantity):
                    entries.append(PhotoTags(photo_id=pid, tag_id=tid))

        PhotoTags.objects.bulk_create(entries, 2000)

    def _build_likes(self):
        '''
        Метод произвольно генерирует лайки пользователей.
        "От имени" каждого из пользователей генерируется примерно 50
        лайков с предпочтением к положительным.

        '''

        user_ids = [self._user_index[key] for key in self._user_index.keys()]
        entries = []
        for uid in user_ids:
            like_quantity = round(random.normalvariate(50, 5))
            if like_quantity > 0:
                for pid in random.sample(self._photo_ids, like_quantity):
                    # Оценка тяготеет к положительной
                    rating = random.choice([1, 1, 1, -1])
                    like = Like(photo_id=pid, user_id=uid, rating=rating)
                    entries.append(like)

        Like.objects.bulk_create(entries, 2000)

    @transaction.atomic
    def _calc_rating(self):
        '''
        Райсчет рейтингов фотографий и заполнение денормализованного
        поля rating.

        '''

        ratings = Photo.objects.annotate(like_rating=Sum('likes__rating')).values('pk', 'like_rating')
        for result in ratings:
            score = result['like_rating'] or 0
            Photo.objects.filter(pk=result['pk']).update(rating=score)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        importer = Importer()
        importer.import_data()
        print('Done')
