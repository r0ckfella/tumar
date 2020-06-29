from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings  # noqa

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


from configurations import importer  # noqa

importer.install()

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tumar.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Production")

app = Celery("tumar-tasks")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery beat
app.conf.beat_schedule = {
    "scheduled": {
        "task": "tumar.animals.tasks.task_download_latest_geolocations",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": "tumar_celerybeat"},
    }
}
