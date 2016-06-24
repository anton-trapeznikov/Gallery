Установка
---------

* Удобным способом создать БД в MySQL и установить привелегии необходимому пользователю. Например, так

```
    CREATE DATABASE <dbname> CHARACTER SET utf8 COLLATE utf8_general_ci;
    GRANT ALL PRIVILEGES ON <dbname>.* TO `<user>` WITH GRANT OPTION;
```

* Создать виртуальное окружение `py3k`

```
    virtualenv --python=python3 [path_to_venv]
```

Возможно, что для установки mysqlclient потребуется установка `python3-dev` и клиентских библиотек mysql. В Debian и его форках - пакеты `mysql-client` и `libmysqlclient-dev`.

* Находясь в виртуальном окружении установить зависимости

```
    pip install -r requirements.txt
```

* Переименовать файл `gallery/local_settings.py.dist` в `gallery/local_settings.py` и настроить в нем параметры подключения к БД.

* Выполнить миграции

```
    python manage.py migrate
```

* Собрать статику

```
    python manage.py collectstatic
```

* Создать суперпользователя

```
    python manage.py createsuperuser
```

* Имортировать данные

```
    python manage.py import_data
```

Эта команда (класс-импортер находится в `gallery.management.commands.import_data.Importer`) выгрузит данные из файла, находящегося в `test_data/test_photo.csv`. В самом файле ~ 10^5 сущностей. Если необходимо, чтобы на сайте было 10^6 сущностей, то, в методе init класса `Importer`, необходимо установить значение 10 атрибуту `self._multiplier` (по умолчанию self._multiplier = 10). Время загрузки миллиона сущностей ~ 30 минут. 100 000 ~ 5 минут.

