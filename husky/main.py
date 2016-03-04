from husky.tasks.stock_quote_tasks import crawl_nasdaq_stock_quote
from husky.tasks.stock_quote_tasks import spider_task
from husky.api import nasdaq
from husky.models.mongo_model import mongo_client, StockQuoteMongoModel
#StockQuoteMongoModel(mongo_client).init_db()
#crawl_nasdaq_stock_quote.delay(nasdaq.PRE_MARKET_QUOTE, "baba")
#print spider_task.delay("http://www.nasdaq.com/zh/symbol/baba/premarket?time=4&page=1", True, 3, None).get()
from husky.tasks.stock_history_tasks import update_all_stock_history
from husky.models.mongo_model import StockHistoryMongoModel

StockHistoryMongoModel(mongo_client).init_db()

update_all_stock_history.delay()