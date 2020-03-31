import os
import dj_database_url

from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True

    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS
    INSTALLED_APPS += ('django_nose',)
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = [
        BASE_DIR,
        # '-s',
        '--nologcapture',
        '--with-coverage',
        '--with-progressive',
        '--cover-package=tumar'
    ]

    # Mail
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # CELERY SETTINGS
    CELERY_BROKER_URL = 'redis://redis:6380/0'
    CELERY_RESULT_BACKEND = 'redis://redis:6380/0'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Almaty'


    # Postgres
    DATABASES = {
        'default': dj_database_url.config(
            default='postgis://postgres:01470258@postgres:5432/postgres',
            conn_max_age=int(os.getenv('POSTGRES_CONN_MAX_AGE', 600))
        ),
        'imagination': dj_database_url.config(
            default='postgis://lgblkb:Dikalyaka2!@postgis:5432/imagination',
            conn_max_age=int(os.getenv('POSTGRES_CONN_MAX_AGE', 600))
        ),
        'egistic_2': dj_database_url.config(
            default='postgis://docker:docker@94.247.135.91:8086/egistic_2.0',
            conn_max_age=int(os.getenv('POSTGRES_CONN_MAX_AGE', 600))
        )
    }

    USE_TZ = False