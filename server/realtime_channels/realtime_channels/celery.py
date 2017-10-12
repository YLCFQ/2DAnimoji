#http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

from __future__ import absolute_import
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtime_channels.settings')

from django.conf import settings

app = Celery('realtime_channels')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)