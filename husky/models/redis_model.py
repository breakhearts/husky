from __future__ import absolute_import
import redis
from husky.api import nasdaq
from husky.settings import settings
import json
import time


def get_redis_client(host, port, db):
    client = redis.StrictRedis(host=host, port=port, db=db)
    return client

redis_client = get_redis_client(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)


class StockQuoteRedisModel(object):
    """
    Use real time quote as example:
    husky:real_time_quote:[date]:[stock]:[time]:data = {
        "1" : [(14:45:31 20.13 12323),(14:45:32 20.14 12332),(14:45:21 20.15 23434)],  // as hash table
            ......,
        "13" : [(14:45:31 20.13 12323),(14:45:32 20.14 12332),(14:45:21 20.15 23434)]
    }
    husky:real_time_quote:[date]:[stock]:[time]:info = { //as hash table
        "total" : 15,               //total pages
        "status" : STATUS_FINISHED
    husky:real_time_quote:[date]:tasks = {
        "BIDU": 0
        "FB": 1
        "MS": 1
    }
    """
    STATUS_INIT = 0
    STATUS_FINISHED = 1

    def __init__(self, client):
        self.client = client

    def _key_prefix(self, type, date, stock, time):
        if type == nasdaq.REAL_TIME_QUOTE:
            return "husky:real_time_quote:{0}:{1}:{2}".format(date, stock, time)
        elif type == nasdaq.AFTER_HOUR_QUOTE:
            return "husky:after_hour_quote:{0}:{1}:{2}".format(date, stock, time)
        elif type == nasdaq.PRE_MARKET_QUOTE:
            return "husky:pre_market_quote:{0}:{1}:{2}".format(date, stock, time)
        return ""

    def _info_key(self, type, date, stock, time):
        return self._key_prefix(type, date, stock, time) + ":info"

    def _data_key(self, type, date, stock, time):
        return self._key_prefix(type, date, stock, time) + ":data"

    def remove_stock(self, type, stock, date):
        """
        clean all data
        """
        for _time in range(1, nasdaq.get_time_slice_max(type) + 1):
            data_key = self._data_key(type, date, stock, _time)
            info_key = self._info_key(type, date, stock, _time)
            self.client.delete(data_key)
            self.client.delete(info_key)

    def save_page_result(self, type, stock, date, time, page, total, data):
        """
        save time quote page result
        """
        data_key = self._data_key(type, date, stock, time)
        info_key = self._info_key(type, date, stock, time)
        self.client.hset(data_key, page, json.dumps(data))
        if page == 1:
            self.client.hset(info_key, "total", total)
            self.client.hset(info_key, "status", StockQuoteRedisModel.STATUS_INIT)
        self._check_finish(data_key, info_key)

    def _check_finish(self, data_key, info_key):
        status = self.client.hget(info_key, "status")
        if status and int(status) == StockQuoteRedisModel.STATUS_FINISHED:
            return True
        total = self.client.hget(info_key, "total")
        total = total and int(total) or 0
        if self.client.hlen(data_key) == total:
            self.client.hset(info_key, "status", StockQuoteRedisModel.STATUS_FINISHED)
            return True
        return False

    def check_time_finish(self, type, stock, date, time):
        data_key = self._data_key(type, date, stock, time)
        info_key = self._info_key(type, date, stock, time)
        return self._check_finish(data_key, info_key)

    def check_stock_finish(self, type, stock, date):
        for _time in range(1, nasdaq.get_time_slice_max(type) + 1):
            if not self.check_time_finish(type, stock, date, _time):
                return False
        return True

    def _load_time_data(self, type, stock, date, time):
        data_key = self._data_key(type, date, stock, time)
        t = self.client.hgetall(data_key)
        return t

    def load_stock(self, type, stock, date):
        data = []
        for i in range(1, nasdaq.get_time_slice_max(type) + 1):
            _time = nasdaq.get_time_slice_max(type) - i + 1
            if not self.check_time_finish(type, stock, date, _time):
                return None
            t = self._load_time_data(type, stock, date, _time)
            keys = [int(key) for key in t.keys()]
            keys.sort()
            for key in keys:
                data.extend(json.loads(t[str(key)]))
        data.reverse()
        return data

    def _task_key(self, type, date, stock):
        if type == nasdaq.REAL_TIME_QUOTE:
            return "husky:real_time_quote:tasks:{0}:{1}".format(date, stock)
        elif type == nasdaq.AFTER_HOUR_QUOTE:
            return "husky:after_hour_quote:tasks:{0}:{1}".format(date, stock)
        elif type == nasdaq.PRE_MARKET_QUOTE:
            return "husky:pre_market_quote:tasks:{0}:{1}".format(date, stock)
        return ""

    def begin_stock_task(self, _type, date, stock):
        key = self._task_key(_type, date, stock)
        self.client.set(key, "0")

    def end_stock_task(self, _type, date, stock):
        key = self._task_key(_type, date, stock)
        self.client.set(key, "1")

    def stock_task_finished(self, _type, date, stock):
        key = self._task_key(_type, date, stock)
        t = self.client.get(key)
        if t == "1":
            return True
        else:
            return False

    def stock_task_started(self, _type, date, stock):
        key = self._task_key(_type, date, stock)
        t = self.client.get(key)
        if t == "1" or t == "0":
            return True
        else:
            return False

def get_timer():
    _pre_time = [0]
    def timer():
        t = time.time()
        p = _pre_time[0]
        _pre_time[0] = t
        if _pre_time:
            return t - p
        return 0
    return timer