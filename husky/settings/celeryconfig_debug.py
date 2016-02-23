BROKER_URL = 'sqla+sqlite:///celerydb.sqlite'
CELERY_RESULT_BACKEND = 'db+sqlite:///results.sqlite'
CELERY_ACCEPT_CONTENT = ['json','pickle']
CELERY_RESULT_SERIALIZER='json'