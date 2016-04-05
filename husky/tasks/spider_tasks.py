from __future__ import absolute_import
from husky.tasks.celery import app
from celery.utils.log import get_task_logger
import requests
from husky.utils import utility
from husky.rpc.client import get_rpc_client
from husky.models.mongo_model import mongo_client, FailedTaskModel
from celery import Task
logger = get_task_logger(__name__)


class SpiderTask(Task):
    abstract = True
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        model = FailedTaskModel(mongo_client)
        model.add("husky.tasks.spider_tasks.spider_task", repr(args), repr(kwargs), repr(einfo))


@app.task(base=SpiderTask, bind=True, max_retries=100, default_retry_delay=1)
def spider_task(self, page_url, use_proxy, timeout, ext):
    logger.debug("start spider page,page_url = %s,id=%s,retries=%d", page_url, self.request.id, self.request.retries)
    rpc_client = None
    proxy_url = None
    transport = None
    try:
        if use_proxy:
            transport, rpc_client = get_rpc_client()
            proxy_url = rpc_client.req_proxy(page_url)
    except Exception as exc:
        logger.error("request proxy error,page_url = %s", page_url)
        raise self.retry(exc=exc)
    try:
        if proxy_url:
            proxies = {
                "http": proxy_url
            }
        else:
            proxies = {}
        headers = {
            "user-agent": utility.random_ua()
        }
        try:
            r = requests.get(page_url, proxies=proxies, headers=headers, timeout = timeout)
        except Exception as exc:
            logger.error("request error, page_url = %s", page_url)
            if rpc_client:
                rpc_client.free_proxy(proxy_url, float("inf"))
            raise exc
        if r.status_code != 200:
            logger.error("spider page status_code not 200,page_url = %s,status_code = %d", page_url, r.status_code)
            if rpc_client:
                rpc_client.free_proxy(proxy_url, float("inf"))
            if transport:
                transport.close()
            return r.status_code, None, ext
        else:
            if rpc_client:
                rpc_client.free_proxy(proxy_url, r.elapsed.total_seconds())
            logger.debug("spider page ok,page_url = %s", page_url)
            if transport:
                transport.close()
            return r.status_code, r.content, ext
    except Exception as exc:
        logger.debug("spider page error,page_url = %s", page_url)
        if transport:
            transport.close()
        raise self.retry(exc=exc)