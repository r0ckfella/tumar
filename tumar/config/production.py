import os

import dj_database_url

from .common import Common


class Production(Common):
    INSTALLED_APPS = Common.INSTALLED_APPS
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    # INSTALLED_APPS += ("gunicorn", )

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    # http://django-storages.readthedocs.org/en/latest/index.html
    # INSTALLED_APPS += ('storages',)
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # AWS_ACCESS_KEY_ID = os.getenv('DJANGO_AWS_ACCESS_KEY_ID')
    # AWS_SECRET_ACCESS_KEY = os.getenv('DJANGO_AWS_SECRET_ACCESS_KEY')
    # AWS_STORAGE_BUCKET_NAME = os.getenv('DJANGO_AWS_STORAGE_BUCKET_NAME')
    # AWS_DEFAULT_ACL = 'public-read'
    # AWS_AUTO_CREATE_BUCKET = True
    # AWS_QUERYSTRING_AUTH = False
    # MEDIA_URL = f'https://s3.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/'

    # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching#cache-control
    # Response can be cached by browser and any intermediary caches (i.e. it is "public") for up to 1 day
    # 86400 = (60 seconds x 60 minutes x 24 hours)
    # AWS_HEADERS = {
    #     'Cache-Control': 'max-age=86400, s-maxage=86400, must-revalidate',
    # }
    STATIC_ROOT = '/static/'

    # Postgis
    DATABASES = {
        'default': dj_database_url.config(
            default='postgis://docker:docker@db_default:5432/tumar',
            conn_max_age=int(os.getenv('POSTGRES_CONN_MAX_AGE', 600))
        ),
        'egistic_2': dj_database_url.config(
            default='postgis://docker:docker@94.247.135.91:8086/egistic_2.0',
            conn_max_age=int(os.getenv('POSTGRES_CONN_MAX_AGE', 600))
        )
    }

    # CELERY SETTIGS
    broker_username = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
    broker_password = os.environ.get(
        'RABBITMQ_DEFAULT_PASS', 'GtzYz4ahBvR3THg6x89E7wpNDCtYGLCZt6LSqZNXWaerEqD3bdkxRqTjZ6DFjL6Z')

    CELERY_BROKER_URL = f'amqp://{broker_username}:{broker_password}@rabbitmq:5672//'
    CELERY_RESULT_BACKEND = 'rpc://'

    # Celery Data Format
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    imports = ('indicators.tasks',)

    CELERY_TASK_ACKS_LATE = False
    CELERY_TASK_QUEUE_MAX_PRIORITY = 10
    CELERY_CREATE_MISSING_QUEUES = True
    CELERY_TASK_REMOTE_TRACEBACKS = True
    CELERY_TASK_DEFAULT_QUEUE = "tumar_queue"
