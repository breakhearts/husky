from __future__ import absolute_import
from husky.asynctasks.celery import app
from husky.asynctasks.tasks import add

def worker_main():
    app.worker_main()