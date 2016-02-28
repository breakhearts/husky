from celery import Celery

app = Celery("tasks")
app.config_from_object("celeryconfig")

@app.task(bind = True)
def add(self, a, b):
    return a + b