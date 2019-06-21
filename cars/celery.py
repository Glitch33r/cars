from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

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
    'add-every-5-seconds': {
        'task': 'extuser.tasks.add',
        'schedule': 5.0,
        'args': (16, 16)
    },
    'add-every-10-seconds': {
        'task': 'extuser.tasks.mul',
        'schedule': 10.0,
        'args': (10, 10)
    },
    'add-every-15-seconds': {
        'task': 'extuser.tasks.xsum',
        'schedule': 15.0,
        'args': (10, 20)
    },
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
