from husky.asynctasks.stock_tasks import crawl_nasdaq_stock_quote
from husky.api import nasdaq

crawl_nasdaq_stock_quote.delay(nasdaq.REAL_TIME_QUOTE, "baba")

