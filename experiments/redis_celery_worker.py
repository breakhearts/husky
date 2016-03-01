from celery import Celery

app = Celery("tasks")
app.config_from_object("celeryconfig")

@app.task(bind = True)
def add(self, a, b):
    return a + b

from celery import Task
class ParseStockQuotePageTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print "***********",len(kwargs), "***************"

@app.task(base=ParseStockQuotePageTask, bind = True)
def exp(self, a, b):
    raise Exception()

app.worker_main()