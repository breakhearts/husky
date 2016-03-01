BROKER_URL = 'redis://192.168.1.100:6379/0'
CELERY_RESULT_BACKEND = 'redis://192.168.1.100:6379/0'
CELERY_ACCEPT_CONTENT = ['json','pickle']
CELERY_RESULT_SERIALIZER='json'
CELERY_REDIRECT_STDOUTS_LEVEL = "info"
CELERY_IGNORE_RESULT = True
CELERY_DISABLE_RATE_LIMITS = True
BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True ,'fanout_patterns': True, 'visibility_timeout': 43200}

from celery.schedules import crontab
CELERY_TIMEZONE = 'US/Eastern'
CELERYBEAT_SCHEDULE = {
    # Executes every Monday morning at 7:30 A.M
    'crawl-nasdaq-stock-time-quote': {
        'task': 'husky.tasks.stock_tasks.crawl_nasdaq_stock_quote_batch',
        'schedule': crontab(hour=17, minute=0, day_of_week = '1-5')
    },
}