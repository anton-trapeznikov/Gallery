from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from gallery.models import *
import random
import uuid
import time
import csv
import os

class Importer(object):
    def __init__(self):

        # Чтение csv
        data_file = os.path.join(settings.BASE_DIR, 'test_data', 'test-photo.csv')
        self._data = []
        if os.path.exists(data_file) and os.path.isfile(data_file):
            with open(data_file, 'r') as f:
                self._data = list(csv.reader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL))

        # Словарь для быстрого сопоставления внешнего и внутреннего
        # id пользователя, где ключ - id в csv, а значение - pk экземпляра модели.
        self._user_index = {}

        self._photo_ids = []

        self._url_validator = URLValidator()

    def import_data(self):
        if self._data:
            self._clear_db()
            self._import_users()
            self._build_user_index()
            self._import_photo()
            self._build_photo_ids()
            self._build_tags()
            self._tag_photo()
            self._build_likes()

    def _clear_db(self):
        User.objects.all().exclude(is_staff=True).delete()
        Photo.objects.all().delete()
        Tag.objects.all().delete()

    def _import_users(self):
        external_user_ids = set([r[0] for r in self._data])

        users = []
        for id in external_user_ids:
            user = User(username='u%s' % id)
            user.set_password(uuid.uuid4().hex[:8])
            users.append(user)

        User.objects.bulk_create(users, 2000)

    def _build_user_index(self):
        self._user_index = {u.username[1:]:u.pk for u in User.objects.all().only('pk', 'username')}

    def _import_photo(self):
        photos = []
        r = 0
        user_ids = self._user_index.keys()
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
        self._photo_ids = [p.pk for p in Photo.objects.all().only('pk')]

    def _build_tags(self):
        tags = [Tag(name='Tag №%s' % tag_no) for tag_no in range(1,100)]
        Tag.objects.bulk_create(tags, 2000)

    def _tag_photo(self):
        tag_ids = [t.pk for t in Tag.objects.all().only('pk')]

        entries = []

        for pid in self._photo_ids:
            # Количество тегов
            tag_quantity = round(random.normalvariate(5,1))
            if tag_quantity > 0:
                for tid in random.sample(tag_ids, tag_quantity):
                    entries.append(PhotoTags(photo_id=pid, tag_id=tid))

        PhotoTags.objects.bulk_create(entries, 2000)

    def _build_likes(self):
        user_ids = [self._user_index[key] for key in self._user_index.keys()]
        entries = []
        for uid in user_ids:
            like_quantity = round(random.normalvariate(30,5))
            if like_quantity > 0:
                for pid in random.sample(self._photo_ids, like_quantity):
                    entries.append(Like(photo_id=pid, user_id=uid, rating=random.choice([1,1,1,-1])))

        Like.objects.bulk_create(entries, 2000)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        importer = Importer()
        importer.import_data()
