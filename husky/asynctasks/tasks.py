from __future__ import absolute_import
from husky.asynctasks.celery import app

@app.task
def add(a,b):
    return a+b