from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cars.settings')

app = Celery('cars')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update_autoRia_every_hour': {
        'task': 'parsers.tasks.upd_ria',
        'schedule': crontab(minute=48, hour='*/2'),
        'args': (2,)
    },
    'check_is_active_users': {
        'task': 'parsers.tasks.check_is_active_users',
        'schedule': crontab(hour=0, minute=0)
        # 'args': (2,)
    },
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
