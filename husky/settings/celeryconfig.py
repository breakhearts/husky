from celery.schedules import crontab
from husky.api import nasdaq
from kombu import Queue, Exchange
BROKER_URL = 'redis://192.168.1.100:6379/0'
CELERY_RESULT_BACKEND = 'redis://192.168.1.100:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER='json'
CELERY_REDIRECT_STDOUTS_LEVEL = "info"
CELERY_IGNORE_RESULT = True
CELERY_DISABLE_RATE_LIMITS = True
BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True, 'fanout_patterns': True, 'visibility_timeout': 43200}
CELERY_TIMEZONE = 'US/Eastern'
CELERYBEAT_SCHEDULE = {
    'crawl-nasdaq-stock-time-quote': {
        'task': 'husky.tasks.stock_tasks.crawl_nasdaq_stock_quote_batch',
        'schedule': crontab(hour=17, minute=0, day_of_week='1-5'),
        'args': (nasdaq.REAL_TIME_QUOTE,)
    },
}

CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('spider_tasks', Exchange('spider_task', routing_key='spider_tasks.#')),
        Queue('stock_tasks', Exchange('stock_task', routing_key='stock_tasks.#'))
)


CELERY_ROUTES = {
    'husky.tasks.spider_tasks.spider_task': {
        'queue': 'spider_tasks',
        'routing_key': 'spider_tasks.spider_task'
    },
    'husky.task.stock_tasks.crawl_nasdaq_stock_quote': {
        'queue': 'stock_tasks',
        'routing_key': 'stock_tasks.crawl_nasdaq_stock_quote'
    },
    'husky.task.stock_tasks.parse_stock_quote_page': {
        'queue': 'stock_tasks',
        'routing_key': 'stock_tasks.parse_stock_quote_page'
    },
    'husky.task.stock_tasks.save_stock_quote_result': {
        'queue': 'stock_tasks',
        'routing_key': 'stock_tasks.save_stock_quote_result'
    },
    'crawl_nasdaq_stock_quote_batch': {
        'queue': 'stock_tasks',
        'routing_key': 'stock_tasks.crawl_nasdaq_stock_quote_batch'
    }
}
