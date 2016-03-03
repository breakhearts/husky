from husky.models.mongo_model import StockQuoteTaskMongoModel, mongo_client
from husky.tasks.stock_quote_tasks import crawl_nasdaq_stock_quote

@app.task(bind = True)
def crawl_nasdaq_stock_quote_batch(self, _type):
    mongo_model = StockQuoteTaskMongoModel(mongo_client)
    for stock in mongo_model.load_stocks():
        crawl_nasdaq_stock_quote(_type, stock)