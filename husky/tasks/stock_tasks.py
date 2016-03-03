from __future__ import absolute_import
from husky.tasks.celery import app
from husky.api import nasdaq
from husky.settings import settings
from husky.tasks.spider_tasks import spider_task
from celery.utils.log import get_task_logger
from husky.models.mongo_model import mongo_client, StockQuoteTaskMongoModel, FailedTaskModel
from husky.models.file_models import StockQuoteFileModel
from husky.models.redis_model import redis_client, StockQuoteRedisModel
from celery import Task
import json

logger = get_task_logger(__name__)

@app.task(bind = True)
def crawl_nasdaq_stock_quote(self, _type, stock):
    logger.debug("start crawl stock quote,type=%d,stock=%s",_type,stock)
    page_url = nasdaq.quote_slice_url_by_type(_type, stock, 1, 1)
    ext = {
        "type" : _type,
        "stock" : stock,
        "time" : 1,
        "page" : 1,
        "retries" : 0
    }
    logger.debug("start spider_task,type=%d,page_url=%s",_type,page_url)
    spider_task.apply_async((page_url, settings.STOCK_SPIDER_USE_PROXY, settings.STOCK_SPIDER_TASK_TIMEOUT,ext),
                            link = parse_stock_quote_page.s())

class ParseStockQuotePageTask(Task):
    abstract = True
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        model = FailedTaskModel(mongo_client)
        model.add("husky.tasks.stock_tasks.parse_stock_quote_page", repr(args), repr(kwargs), repr(einfo))

@app.task(base = ParseStockQuotePageTask, bind = True)
def parse_stock_quote_page(self, args):
    status_code, content, ext = args
    _type,stock,time,page = ext["type"], ext["stock"], ext["time"], ext["page"]
    logger.debug("parse stock quote page,status_code=%d,type=%d,stock=%s,time=%d,page=%d,id=%s",status_code,_type,stock,time,page,self.request.id)
    def _re_crawl_page():
        if ext["retries"] < settings.STOCK_SPIDER_MAX_RETRY:
            ext["retries"] += 1
            page_url = nasdaq.quote_slice_url_by_type(_type, stock, time, page)
            logger.debug("_re_crawl_page,type=%d,page_url=%s,retries=%d",_type,page_url,ext["retries"])
            spider_task.apply_async((page_url, settings.STOCK_SPIDER_USE_PROXY, settings.STOCK_SPIDER_TASK_TIMEOUT,ext),
                                    link = parse_stock_quote_page.s())
        else:
            logger.debug("max retries failed,status_code=%d,type=%d,stock=%s,time=%d,page=%d",status_code,_type,stock,time,page)
            save_failed_time_quote_task(_type, stock, time, page, "STOCK_SPIDER_MAX_RETRY HIT")

    if status_code != 200:
        _re_crawl_page()
        return
    try:
        date, data, current, first, last = nasdaq.parse_time_quote_slice_page(content)
    except Exception as exc:
        if isinstance(exc, nasdaq.NoTradingDataException):
            pass
        else:
            _re_crawl_page()
        return
    if ext["page"] == 1:
        # start crawl other pages
        for page_no in range(2, last + 1):
            page_url = nasdaq.quote_slice_url_by_type(_type, stock, time, page_no)
            c_ext = {
                "type" : _type,
                "stock" : stock,
                "time" : time,
                "page" : page_no,
                "retries" : 0
            }
            logger.debug("start spider_task,type=%d,page_url=%s",_type,page_url)
            spider_task.apply_async((page_url, settings.STOCK_SPIDER_USE_PROXY, settings.STOCK_SPIDER_TASK_TIMEOUT,c_ext),
                                    link = parse_stock_quote_page.s())
        if ext["time"] == 1:
            # start crawl other times
            for time_no in range(2, nasdaq.get_time_slice_max(_type) + 1):
                page_url = nasdaq.quote_slice_url_by_type(_type, stock, time_no, 1)
                c_ext = {
                    "type" : _type,
                    "stock" : stock,
                    "time" : time_no,
                    "page" : 1,
                    "retries" : 0
                }
                logger.debug("start spider_task,type=%d,page_url=%s",_type,page_url)
                spider_task.apply_async((page_url, settings.STOCK_SPIDER_USE_PROXY, settings.STOCK_SPIDER_TASK_TIMEOUT,c_ext),
                                        link = parse_stock_quote_page.s())
    save_stock_quote_result.apply_async((_type, date, stock, time, page, last, data))

class SaveStockQuoteResultTask(Task):
    abstract = True
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        model = FailedTaskModel(mongo_client)
        model.add("husky.tasks.stock_tasks.save_stock_quote_result", repr(args), repr(kwargs), repr(exc))

@app.task(base = SaveStockQuoteResultTask, bind = True)
def save_stock_quote_result(self, type, date, stock, time, page, total_pages, data):
    redis_model = StockQuoteRedisModel(redis_client)
    if time == 1 and page == 1:
        redis_model.remove_stock(type, stock, date)
    redis_model.save_page_result(type, stock, date, time, page, total_pages, data)
    if redis_model.check_stock_finish(type, stock, date):
        file_model = StockQuoteFileModel(settings.STOCK_QUOTE_ROOT)
        t = redis_model.load_stock(type, stock, date)
        file_model.remove_stock(type, stock, date)
        file_model.save_stock_quote(type, stock, date, t)
    logger.debug("save stock_quote,%d %s %s %d %d %d %s", type, date, stock, time, page, total_pages, json.dumps(data))

@app.task(bind = True)
def crawl_nasdaq_stock_quote_batch(self, _type):
    mongo_model = StockQuoteTaskMongoModel(mongo_client)
    for stock in mongo_model.load_stocks():
        crawl_nasdaq_stock_quote(_type, stock)

def save_failed_time_quote_task(_type, stock, _time, page, reason):
    model = FailedTaskModel(mongo_client)
    model.add("time_quote_task", "", {
        "type": _type,
        "time": _time,
        "page": page
    }, reason)
