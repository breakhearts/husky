from celery.schedules import crontab
from husky.api import nasdaq
from kombu import Queue, Exchange
BROKER_URL = 'redis://192.168.1.100:6379/0'
CELERY_RESULT_BACKEND = 'redis://192.168.1.100:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIRECT_STDOUTS_LEVEL = "info"
CELERY_IGNORE_RESULT = True
CELERY_DISABLE_RATE_LIMITS = True
BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True, 'fanout_patterns': True, 'visibility_timeout': 43200}
CELERY_TIMEZONE = 'US/Eastern'
CELERYBEAT_SCHEDULE = {
    'update_real_time_quote': {
        'task': 'husky.tasks.stock_quote_tasks.crawl_nasdaq_stock_quote_batch',
        'schedule': crontab(hour=17, minute=0, day_of_week='1-5'),
        'args': (nasdaq.REAL_TIME_QUOTE,)
    },
    'update_history': {
        'task': 'husky.tasks.stock_history_tasks.update_history',
        'schedule': crontab(hour=0, minute=0, day_of_week='1-5')
    },
}

CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('spider_tasks', Exchange('spider_task', type='topic'), routing_key='spider_tasks.#'),
    Queue('stock_quote_tasks', Exchange('stock_quote_tasks', type='topic'), routing_key='stock_quote_tasks.#'),
    Queue('stock_history_tasks', Exchange('stock_history_tasks', type='topic'), routing_key='stock_history_tasks.#')
)


CELERY_ROUTES = {
    'husky.tasks.spider_tasks.spider_task': {
        'queue': 'spider_tasks',
        'routing_key': 'spider_tasks.spider_task'
    },
    'husky.tasks.stock_quote_tasks.crawl_nasdaq_stock_quote': {
        'queue': 'stock_quote_tasks',
        'routing_key': 'stock_quote_tasks.crawl_nasdaq_stock_quote'
    },
    'husky.tasks.stock_quote_tasks.parse_stock_quote_page': {
        'queue': 'stock_quote_tasks',
        'routing_key': 'stock_quote_tasks.parse_stock_quote_page'
    },
    'husky.tasks.stock_quote_tasks.save_stock_quote_result': {
        'queue': 'stock_quote_tasks',
        'routing_key': 'stock_quote_tasks.save_stock_quote_result'
    },
    'husky.tasks.stock_quote_tasks.crawl_nasdaq_stock_quote_batch': {
        'queue': 'stock_quote_tasks',
        'routing_key': 'stock_quote_tasks.crawl_nasdaq_stock_quote_batch'
    },
    'husky.tasks.stock_history_tasks.update_all_stock_history': {
        'queue': 'stock_history_tasks',
        'routing_key': 'stock_history_tasks.update_all_stock_history'
    },
    'husky.tasks.stock_history_tasks.parse_stock_history': {
        'queue': 'stock_history_tasks',
        'routing_key': 'stock_history_tasks.parse_stock_history'
    }
}
