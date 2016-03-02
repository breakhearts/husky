import pytest
from husky.models.redis_model import *
from husky.models.mongo_model import *
@pytest.fixture(scope="module")
def redis_client(request):
    client = get_redis_client("localhost","6379",0)
    return client

@pytest.fixture(scope="module")
def mongo_client(request):
    client = get_mongo_client("localhost", 27017)
    return client

class TestStockQuoteRedisModel:
    def test_all(self,redis_client):
        stock_redis = StockQuoteRedisModel(redis_client)
        for _type in (nasdaq.REAL_TIME_QUOTE, nasdaq.PRE_MARKET_QUOTE, nasdaq.AFTER_HOUR_QUOTE):
            stock_redis.remove_stock(_type, "baba", "2013-10-25")
            for _time in range(1,nasdaq.get_time_slice_max(nasdaq.REAL_TIME_QUOTE) + 1):
                import random
                total_page = random.randint(1,10)
                for page in range(1, total_page + 1):
                    stock_redis.save_page_result(_type, "baba", "2013-10-25", _time, page, total_page, [("15:%02d:%02d" %(_time, total_page - page),25.13,_time * 100000 + (total_page - page) * 10 + 1),("15:%02d:%02d" %(_time, total_page - page),25.13,_time * 100000 + (total_page - page)*10)])
                    if page != total_page:
                        assert not stock_redis.check_time_finish(_type, "baba", "2013-10-25", _time)
            assert stock_redis.check_stock_finish(_type, "baba", "2013-10-25")
            t = stock_redis.load_stock(_type, "baba", "2013-10-25")
            from copy import deepcopy
            t1 = deepcopy(t)
            t1.sort(key = lambda x:x[-1])
            assert t == t1

class TestStockQuoteMongoModel:
    def test_all(self,mongo_client):
        model = StockQuoteMongoModel(mongo_client)
        model.init_db()
        for _type in (nasdaq.REAL_TIME_QUOTE, nasdaq.PRE_MARKET_QUOTE, nasdaq.AFTER_HOUR_QUOTE):
            model.save_stock_quote(_type, "baba", "2013-12-11", [[u'15:01:11', 25.13, 100000], [u'15:01:10', 25.13, 100001], [u'15:01:12', 25.13, 100010], [u'15:01:15', 25.13, 100011]])
            t =  model.load_stock_quote(_type, "baba", "2013-12-11")
            assert len(t["data"]) == 4
            model.remove_stock(_type, "baba", "2013-12-11")
            t =  model.load_stock_quote(_type, "baba", "2013-12-11")
            assert not t

class TestStockQuoteTaskModel:
    def test_all(self, mongo_client):
        model = StockQuoteTaskMongoModel(mongo_client)
        model.init_db()
        model.add_stock("baba")
        model.add_stock("bidu")
        assert len(model.load_stocks()) == 2
        model.remove_stock("bidu")
        assert len(model.load_stocks()) == 1

class TestFailedTaskModel:
    def test_all(self, mongo_client):
        model = FailedTaskModel(mongo_client)
        model.init_db()
        model.add("time_quote", "", {
            "stock" : "baba",
            "time" : 1,
            "page" : 1
        }, "sss")

