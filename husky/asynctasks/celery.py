from __future__ import absolute_import
from celery import Celery
from husky.settings import settings

app = Celery("task")
if settings.DEBUG:
    app.config_from_object("husky.settings.celeryconfig_debug")
else:
    app.config_from_object("husky.settings.celeryconfig")