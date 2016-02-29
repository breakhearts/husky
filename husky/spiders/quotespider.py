from husky.api import nasdaq
from celery.utils.log import get_task_logger
from husky.asynctasks.spider_tasks import spider_task, parse_stock_quote_page
from husky.settings import settings

logger = get_task_logger(__name__)



