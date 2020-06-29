import os

import dj_database_url

from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Production(Common):
    INSTALLED_APPS = Common.INSTALLED_APPS
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
    ALLOWED_HOSTS = ["tumarb.winext.kz", "www.tumarb.winext.kz"]
    INSTALLED_APPS += ("django_log_to_telegram",)

    # Postgis
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("TUMAR_DB"),
            conn_max_age=int(os.getenv("POSTGRES_CONN_MAX_AGE", 600)),
        ),
    }

    # CELERY SETTIGS
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

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

    LOG_TO_TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d"
                + " %(message)s"
            },
            "simple": {"format": "[%(levelname)s] %(message)s"},
        },
        "filters": {
            "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
        },
        "handlers": {
            "telegram_log": {
                "level": "ERROR",
                "filters": ["require_debug_false"],
                "class": "django_log_to_telegram.log.AdminTelegramHandler",
                "bot_token": LOG_TO_TELEGRAM_BOT_TOKEN,
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
        "FCM_API_KEY": os.getenv("FCM_API_KEY"),
    }
