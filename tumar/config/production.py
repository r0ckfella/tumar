import os
import sentry_sdk

from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from decouple import config
from dj_database_url import parse as db_url

from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Production(Common):
    INSTALLED_APPS = Common.INSTALLED_APPS
    SECRET_KEY = config("DJANGO_SECRET_KEY")
    ALLOWED_HOSTS = ["tumarb.winext.kz", "www.tumarb.winext.kz"]
    # INSTALLED_APPS += ("",)

    # Postgis
    DATABASES = {
        "default": config("TUMAR_DB", cast=db_url),
    }

    # CELERY SETTIGS
    CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="rpc://")
    CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="rpc://")

    # Celery Data Format
    CELERY_ACCEPT_CONTENT = ["application/json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TIMEZONE = "Asia/Almaty"
    imports = ("indicators.tasks",)

    CELERY_TASK_ACKS_LATE = False
    CELERY_TASK_QUEUE_MAX_PRIORITY = 10
    CELERY_CREATE_MISSING_QUEUES = True
    CELERY_TASK_REMOTE_TRACEBACKS = True
    CELERY_TASK_DEFAULT_QUEUE = "tumar_queue"

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d"
                + " %(message)s"
            },
            "simple": {"format": "[%(levelname)s] %(message)s"},
            "telegram": {
                "class": "telegram_handler.HtmlFormatter",
                "fmt": "<code>%(asctime)s</code> <b>%(levelname)s</b>\n%(message)s",
            },
        },
        "filters": {
            "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
        },
        "handlers": {
            "telegram_log": {
                "level": "ERROR",
                "filters": ["require_debug_false"],
                "class": "telegram_handler.TelegramHandler",
                "token": config("TELEGRAM_BOT_TOKEN"),
                "chat_id": config("TELEGRAM_CHAT_ID"),
                "formatter": "telegram",
            },
            "file": {
                "level": "INFO",
                "filters": ["require_debug_false"],
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(os.path.dirname(BASE_DIR), "info.log"),
                "maxBytes": 1024 * 1024 * 5,  # 5MB
                "backupCount": 5,
                "formatter": "verbose",
            },
            "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        },
        "loggers": {
            "": {"handlers": ["file", "console", "telegram_log"], "level": "INFO"},
        },
    }

    PUSH_NOTIFICATIONS_SETTINGS = {
        "FCM_API_KEY": config("FCM_API_KEY", ""),
        "APNS_CERTIFICATE": config("APNS_CERTIFICATE_PATH", ""),
    }

    sentry_sdk.init(
        dsn=config("SENTRY_DSN", ""),
        integrations=[DjangoIntegration(), CeleryIntegration()],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
