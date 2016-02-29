import pytest
from husky.models.redis_model import *
@pytest.fixture(scope="module")
def redis_client(request):
    client = get_redis_client("localhost","6379",0)
    return client

class TestStockQuoteRedisModel:
    def test_all(self,redis_client):
        stock_redis = StockQuoteRedisModel(redis_client)
        stock_redis.rest(nasdaq.REAL_TIME_QUOTE, "baba", "2013-10-25")
        for _time in range(1,nasdaq.get_time_slice_max(nasdaq.REAL_TIME_QUOTE) + 1):
            import random
            total_page = random.randint(1,10)
            for page in range(1, total_page + 1):
                stock_redis.save_page_result(nasdaq.REAL_TIME_QUOTE, "baba", "2013-10-25", _time, page, total_page, [("15:14:13",25.13,12321),("15:14:15",25.14,12321)])
                if page != total_page:
                    assert not stock_redis.check_time_finish(nasdaq.REAL_TIME_QUOTE, "baba", "2013-10-25", _time)
        assert stock_redis.check_stock_finish(nasdaq.REAL_TIME_QUOTE, "baba", "2013-10-25")