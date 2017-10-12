from __future__ import unicode_literals, absolute_import

from django.db import models
from django.utils import timezone

# Create your models here.
class Job(models.Model):
    img = models.CharField(max_length=8000)
    status = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True, blank=True)
    celery_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ('created',)

    def __unicode__(self):
        return self.name