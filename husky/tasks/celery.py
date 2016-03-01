from __future__ import absolute_import
from celery import Celery

app = Celery("task")
app.config_from_object("husky.settings.celeryconfig")