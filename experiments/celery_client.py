from redis_celery_worker import add, exp
#print add.delay(1,2).get()
print exp.delay(1,2).get()