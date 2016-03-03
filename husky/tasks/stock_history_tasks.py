from __future__ import absolute_import
from husky.tasks.celery import app
from husky.api import nasdaq, yahoo
from husky.models.mongo_model import mongo_client, StockHistoryMongoModel, StockInfo
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@app.task(bind=True)
def update_company_list(self):
    model = StockHistoryMongoModel(mongo_client)
    model.clear_stock_info()
    symbols = []
    try:
        company_list = nasdaq.get_all_company_list()
        for symbol, name, market_cap in company_list:
            stock_info = StockInfo(symbol=symbol, name=name, market_cap=market_cap)
            model.insert_stock_info(stock_info)
            logger.debug("[INSERT STOCK INFO], symbol = %s", symbol)
            symbols.append(symbol)
        logger.debug("[UPDATE COMPANY SUCCESS]")
    except Exception as exc:
        logger.error("[UPDATE COMPANY FAILED]")
        symbols = model.query_stock_symbol(0)
    return symbols


@app.task(bind=True)
def get_stock_history(self):
    pass

