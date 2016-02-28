from __future__ import absolute_import
from husky.asynctasks.celery import app
from husky.api import nasdaq
from husky.settings import settings
from husky.asynctasks.spider_tasks import spider_task
from celery.utils.log import get_task_logger
from celery.result import AsyncResult
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
                            link = parse_stock_quote_page.s(), link_error = spider_task_error_handler.s())

@app.task(bind = True)
def spider_task_error_handler(self, uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=True)
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(uuid, exc, result.traceback))

@app.task(bind = True)
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
                                    link = parse_stock_quote_page.s(), link_error = spider_task_error_handler.s())
        else:
            logger.debug("max retries failed,status_code=%d,type=%d,stock=%s,time=%d,page=%d",status_code,_type,stock,time,page)
            save_failed_task()

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
                                    link = parse_stock_quote_page.s(), link_error = spider_task_error_handler.s())
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
                                        link = parse_stock_quote_page.s(), link_error = spider_task_error_handler.s())
    save_stock_quote_result.apply_async((_type, date, data, stock, time, page, last),
                            link_error = save_stock_quote_error_handler.s())

@app.task(bind = True)
def save_stock_quote_result(self, type, date, data, stock, time, page, total_pages):
    logger.debug("save stock_quote,%d %s %s %d %d %d", type, date, stock, time, page, total_pages)

@app.task(bind = True)
def save_stock_quote_error_handler(self, uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=True)
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(uuid, exc, result.traceback))

def save_failed_task():
    pass