from husky.tasks.stock_quote_tasks import crawl_nasdaq_stock_quote_batch
from husky.tasks.stock_history_tasks import update_all_stock_history
from husky.api import nasdaq
from husky.tasks.celery import app


@app.task(bind=True)
def update_real_time_quote(self):
    crawl_nasdaq_stock_quote_batch(nasdaq.REAL_TIME_QUOTE)


@app.task(bind=True)
def update_history(self):
    update_all_stock_history()
