from __future__ import absolute_import, unicode_literals
import os
import configurations
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tumar.config")
# os.environ.setdefault("DJANGO_CONFIGURATION", "Local")
configurations.setup()

app = Celery('tumar-tasks')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery beat
app.conf.beat_schedule = {
    'scheduled': {
        'task': 'tumar.animals.tasks.task_download_latest_geolocations',
        'schedule': crontab(minute='*/15')
    }
}

#  celery -A tumar worker -l info ---AND--- celery -A tumar beat -l info
