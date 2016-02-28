import os
ROOT_PATH = os.path.abspath(os.path.dirname(__file__) + "../../")

BROKER_URL = 'sqla+sqlite:///' + os.path.join(ROOT_PATH, 'celerydb.sqlite')
CELERY_RESULT_BACKEND = 'db+sqlite:///' + os.path.join(ROOT_PATH, 'resultdb.sqlite')
CELERY_ACCEPT_CONTENT = ['json','pickle']
CELERY_RESULT_SERIALIZER='json'
CELERY_REDIRECT_STDOUTS_LEVEL = "info"
CELERY_IGNORE_RESULT = True
CELERY_DISABLE_RATE_LIMITS = True