from __future__ import absolute_import
from husky.asynctasks.celery import app
from celery.utils.log import get_task_logger
import logging.config
from husky.settings import settings

logger = get_task_logger(__name__)
logging.config.dictConfig(settings.LOG_SETTINGS)

@app.task(bind = True, max_retries = 10, default_retry_default = 0)
def spider_task(self, page_url):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc)