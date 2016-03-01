BROKER_URL = 'redis://192.168.1.100:6379/0'
CELERY_RESULT_BACKEND = 'redis://192.168.1.100:6379/0'
CELERY_ACCEPT_CONTENT = ['json','pickle']
CELERY_RESULT_SERIALIZER='json'
CELERY_REDIRECT_STDOUTS_LEVEL = "info"
CELERY_IGNORE_RESULT = False
CELERY_DISABLE_RATE_LIMITS = True

from celery.schedules import crontab

CELERY_TIMEZONE = 'US/Eastern'
CELERYBEAT_SCHEDULE = {
    # Executes every Monday morning at 7:30 A.M
    'add-every-monday-morning': {
        'task': 'experiments.add',
        'schedule': crontab(hour=9, minute=54),
        'args': (16, 16),
    },
}