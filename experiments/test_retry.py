from celery import Celery
import random
app = Celery("tasks")
app.config_from_object("experiments.celeryconfig")

@app.task(bind = True, max_retries = 100, default_retry_delay = 0)
def add(self, a, b):
    print "****************",self.request.retries, self.request.id
    if self.request.retries == 0:
        raise self.retry()
    return a + b