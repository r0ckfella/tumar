import os

from decouple import config

from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True

    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS
    # INSTALLED_APPS += ("django_nose",)
    # TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
    # NOSE_ARGS = [
    #     BASE_DIR,
    #     # '-s',
    #     "--nologcapture",
    #     "--with-coverage",
    #     "--with-progressive",
    #     "--cover-package=tumar",
    # ]

    Common.REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    )

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # CELERY SETTINGS
    CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="rpc://")
    CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="rpc://")
    CELERY_ACCEPT_CONTENT = ["application/json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TIMEZONE = "Asia/Almaty"

    USE_TZ = False
