from redis_celery_worker import add

print add.delay(1,2).get()