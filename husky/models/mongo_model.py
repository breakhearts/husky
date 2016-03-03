from pymongo import MongoClient
from husky.api import nasdaq
from husky.settings import settings
import pymongo
from datetime import datetime


def get_mongo_client(host, port):
    client = MongoClient(host, port, connect=False)
    return client

mongo_client = get_mongo_client(settings.MONGO_HOST, settings.MONGO_PORT)


class StockQuoteMongoModel(object):
    """
    Use real time quote as example:
    db:
    husky
    collections:
    real_time_quote : {
        "stock" : "baba"
        "date" : 2012-10-15,
        "data" : [(14:45:31 20.13 12323),(14:45:32 20.14 12332),(14:45:21 20.15 23434)]
    }
    """
    def __init__(self, client):
        self.client = client
        self.db = self.client[self.db_name]

    @property
    def db_name(self):
        return "husky"

    def init_db(self):
        for _type in (nasdaq.REAL_TIME_QUOTE, nasdaq.AFTER_HOUR_QUOTE, nasdaq.PRE_MARKET_QUOTE):
            self.db.drop_collection(self.get_collection_name(_type))
            collection = self.db[self.get_collection_name(_type)]
            collection.create_index([('stock', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], unique=True)

    def get_collection_name(self, type):
        if type == nasdaq.REAL_TIME_QUOTE:
            return "real_time_quote"
        elif type == nasdaq.AFTER_HOUR_QUOTE:
            return "after_hour_quote"
        elif type == nasdaq.PRE_MARKET_QUOTE:
            return "pre_market_quote"
        return ""

    def save_stock_quote(self, type, stock, date, data):
        collection = self.db[self.get_collection_name(type)]
        collection.insert({
            "stock": stock,
            "date": date,
            "data": data
        })

    def load_stock_quote(self, type, stock, date):
        collection = self.db[self.get_collection_name(type)]
        t = collection.find_one({
            "stock": stock,
            "date": date
        })
        return t

    def remove_stock(self, type, stock, date):
        collection = self.db[self.get_collection_name(type)]
        collection.remove({"stock":stock, "date":date})


class StockQuoteTaskMongoModel(object):
    """
    monitor stocks:
    db:
    husky
    collections:
    monitor_quote_stocks
    [
        "baba",
        "bidu",
        "yahoo"
    ]
    """
    def __init__(self, client):
        self.client = client
        self.db = self.client[self.db_name]

    @property
    def db_name(self):
        return "husky"

    def init_db(self):
        self.db.drop_collection(self.collection_name)
        collection = self.db[self.collection_name]
        collection.create_index([('symbol', pymongo.ASCENDING),], unique=True)

    @property
    def collection_name(self):
        return "monitor_quote_stocks"

    def add_stock(self, stock):
        collection = self.db[self.collection_name]
        collection.insert({
            "symbol": stock
        })

    def remove_stock(self, stock):
        collection = self.db[self.collection_name]
        collection.remove({
            "symbol": stock
        })

    def load_stocks(self):
        collection = self.db[self.collection_name]
        stocks = []
        for t in collection.find():
            stocks.append(t["symbol"])
        return stocks


class FailedTaskModel(object):
    def __init__(self, client):
        self.client = client
        self.db = self.client[self.db_name]

    def init_db(self):
        self.db.drop_collection(self.collection_name)
        collection = self.db[self.collection_name]
        collection.create_index([('time', pymongo.ASCENDING)])

    @property
    def db_name(self):
        return "husky"

    @property
    def collection_name(self):
        return "failed_tasks"

    def add(self, _type, args, kwargs, reason):
       collection = self.db[self.collection_name]
       collection.insert({
           "type": _type,
           "args": args,
           "kwargs": kwargs,
           "reason": reason,
           "time": datetime.now()
       })

    def get_all(self):
        collection = self.db[self.collection_name]
        return collection.find()

    def init_db(self):
        self.db.drop_collection(self.collection_name)
        collection = self.db[self.collection_name]
        collection.create_index([('symbol', pymongo.ASCENDING), ], unique=True)


class StockInfo(object):
    def __init__(self, **kwargs):
        self.symbol = kwargs["symbol"]
        self.market_cap = kwargs["market_cap"]
        self.name = kwargs["name"]

    @staticmethod
    def from_dict(_dict):
        return StockInfo(**_dict)


class StockDay(object):
    def __init__(self, **kwargs):
        self.symbol = kwargs["symbol"]
        self.date = kwargs["date"]
        self.open = kwargs["open"]
        self.close = kwargs["close"]
        self.high = kwargs["high"]
        self.low = kwargs["low"]
        self.volume = kwargs["volume"]
        self.amount = kwargs["amount"]
        self.adj_close = kwargs["adj_close"]
        self.high_low_amplitude = kwargs["high_low_amplitude"]
        self.close_open_amplitude = kwargs["close_open_amplitude"]
        self.open_change = kwargs["open_change"]
        self.close_change = kwargs["close_change"]
        self.low_change = kwargs["low_change"]
        self.high_change = kwargs["high_change"]

    @staticmethod
    def from_raw_data(symbol, date, last_adj_close, open_, close, high, low, adj_close, volume):
        adj_close = float(adj_close)
        factor = float(close) and float(adj_close) / float(close) or 0
        volume = float(volume)
        high = float(high)
        low = float(low)
        open_ = float(open_)
        close = float(close)
        adj_low = low * factor
        adj_high = high * factor
        adj_open = open_ * factor
        high_low_amplitude = last_adj_close and (adj_high - adj_low) / last_adj_close or 0
        close_open_amplitude = last_adj_close and (adj_open - adj_close) / last_adj_close or 0
        high_change = last_adj_close and (adj_high - last_adj_close) / last_adj_close or 0
        low_change = last_adj_close and (adj_low - last_adj_close) / last_adj_close or 0
        close_change = last_adj_close and (adj_close - last_adj_close) / last_adj_close or 0
        open_change = last_adj_close and (adj_open - last_adj_close) / last_adj_close or 0
        amount = volume * (high + low) / 2
        return StockDay(symbol=symbol, date=date, open = open_, close=close, high=high, low=low, adj_close=adj_close, volume=volume,
                        amount=amount, open_change=open_change, close_change=close_change,high_change=high_change,
                        low_change=low_change, high_low_amplitude=high_low_amplitude, close_open_amplitude=close_open_amplitude)

    @staticmethod
    def from_dict(_dict):
        return StockDay(**_dict)


class StockHistoryMongoModel(object):
    def __init__(self, client):
        self.client = client
        self.db = self.client[self.db_name]
        self.stock_info = self.db[self.company_collection_name]
        self.day_trade = self.db[self.history_collection_name]

    @property
    def db_name(self):
        return "husky"

    @property
    def history_collection_name(self):
        return "history"

    @property
    def company_collection_name(self):
        return "company"

    def init_db(self):
        self.db.drop_collection(self.history_collection_name)
        collection = self.db[self.history_collection_name]
        collection.create_index([('symbol', pymongo.ASCENDING), ('date', pymongo.DESCENDING)], unique=True)

        self.db.drop_collection(self.company_collection_name)
        collection = self.db[self.company_collection_name]
        collection.create_index([('symbol', pymongo.ASCENDING)], unique=True)

    def insert_stock_day(self, stock_day):
        self.day_trade.insert_one(stock_day.__dict__)

    def insert_stock_day_batch(self, stock_days):
        t = []
        for stock_day in stock_days:
            t.append(stock_day.__dict__)
        if t:
            self.day_trade.insert_many(t)

    def insert_stock_info(self, stock_info):
        self.stock_info.insert(stock_info.__dict__)

    def insert_stock_info_batch(self, stock_infos):
        t = []
        for stock_info in stock_infos:
            t.append(stock_info.__dict__)
        if t:
            self.stock_info.insert_many(t)

    def clear_stock_info(self):
        self.stock_info.drop()

    def get_stock_last_day_trade(self, stock):
        t = self.day_trade.find_one({
            "symbol": stock
        })
        if t is None:
            return None
        return t

    def get_stock_last_day_trade(self, stock):
        t = self.day_trade.find_one({
            "symbol": stock
        })
        if t is None:
            return None
        return t

    def query_stock_symbol(self, min_market_cap):
        t = self.stock_info.find({"market_cap": {"$gte": min_market_cap}})
        return [x["symbol"] for x in t]

