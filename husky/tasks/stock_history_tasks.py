from __future__ import absolute_import
from husky.tasks.celery import app
from husky.api import nasdaq, yahoo
from husky.models.mongo_model import mongo_client, StockHistoryMongoModel, StockInfo, FailedTaskModel, StockDay
from celery.utils.log import get_task_logger
from datetime import datetime
from husky.tasks.spider_tasks import spider_task
from husky.settings import settings
from celery.task import Task

logger = get_task_logger(__name__)


def update_company_list():
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
def update_all_stock_history(self):
    model = StockHistoryMongoModel(mongo_client)
    symbols = update_company_list()
    for symbol in symbols:
        t = model.get_stock_last_day_trade(symbol)
        if not t:
            last_adj_close = 0
            last_modify_date = "19700101"
        else:
            last_adj_close = t["adj_close"]
            last_modify_date = datetime.strptime(t["date"], "%Y-%m-%d")
            last_modify_date = last_modify_date.strftime("%Y%m%d")
        page_url = yahoo.get_history_data_url(symbol, start=last_modify_date)
        ext = {"last_adj_close": last_adj_close, "last_modify_date": last_modify_date, "stock": symbol, "retries": 0}
        spider_task.apply_async((page_url, settings.STOCK_SPIDER_USE_PROXY, settings.STOCK_SPIDER_PAGE_TIMEOUT, ext),
                                link=parse_stock_history.s(), expires=settings.STOCK_HISTORY_EXPIRES)
        logger.debug("update stock history,symbol=%s",symbol)


class ParseStockHistoryTask(Task):
    abstract = True
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        model = FailedTaskModel(mongo_client)
        model.add("husky.tasks.stock_quote_tasks.parse_stock_history", repr(args), repr(kwargs), repr(einfo))


@app.task(bind=True, base=ParseStockHistoryTask)
def parse_stock_history(self, args):
    status_code, content, ext = args
    stock, last_modify_date, last_adj_close = ext["stock"], ext["last_modify_date"], ext["last_adj_close"]

    def _re_crawl_page():
        if ext["retries"] < settings.STOCK_SPIDER_MAX_RETRY:
            ext["retries"] += 1
            page_url = yahoo.get_history_data_url(stock, start=last_modify_date)
            spider_task.apply_async((page_url, settings.STOCK_SPIDER_USE_PROXY, settings.STOCK_SPIDER_PAGE_TIMEOUT, ext)
                                    , link=parse_stock_history.s(), expires=settings.STOCK_HISTORY_EXPIRES)
        else:
            logger.debug("max retries failed,symbol = %s", stock)
            save_failed_history_task(stock, reason="STOCK_SPIDER_MAX_RETRY")

    if status_code != 200:
        _re_crawl_page()
        return

    try:
        data = yahoo.parse_history_data(content)
        t = []
        if data:
            for (date, open_, high, low, close, volume, adj_close) in data:
                stock_day = StockDay.from_raw_data(symbol=stock, date=date, last_adj_close=last_adj_close, open_=open_,
                                           close=close, high=high, low=low, adj_close=adj_close, volume=volume)
                t.append(stock_day)
                last_adj_close = stock_day.adj_close
            model = StockHistoryMongoModel(mongo_client)
            model.insert_stock_day_batch(t)
        logger.debug("[TASK SUCCESS]save stock ok, symbol = %s, total = %d", stock, len(data))
    except:
        self.logger.debug_class_fun(self, "[TASK SUCCESS]save stock failed, symbol = %s", stock)
        _re_crawl_page()


def save_failed_history_task(stock, reason):
    model = FailedTaskModel(mongo_client)
    model.add("history_task", "", {
        "stock": stock
    }, reason)
