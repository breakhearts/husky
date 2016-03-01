from pymongo import MongoClient
from husky.api import nasdaq
from husky.settings import settings
import pymongo
from datetime import datetime

def get_mongo_client(host, port):
    client = MongoClient(host, port)
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
        self.db = self.client[self.db_name()]

    def db_name(self):
        return "husky"

    def init_db(self):
        for _type in (nasdaq.REAL_TIME_QUOTE, nasdaq.AFTER_HOUR_QUOTE, nasdaq.PRE_MARKET_QUOTE):
            self.db.drop_collection(self.get_collection_name(_type))
            collection = self.db[self.get_collection_name(_type)]
            collection.create_index([('stock', pymongo.ASCENDING) , ('date', pymongo.ASCENDING)], unique = True)

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
            "stock" : stock,
            "date" : date,
            "data" : data
        })

    def load_stock_quote(self, type, stock, date):
        collection = self.db[self.get_collection_name(type)]
        t = collection.find_one({
            "stock" : stock,
            "date" : date
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
        self.db = self.client[self.db_name()]

    def db_name(self):
        return "husky"

    def init_db(self):
        self.db.drop_collection(self.get_collection_name())
        collection = self.db[self.get_collection_name()]
        collection.create_index([('symbol', pymongo.ASCENDING),], unique = True)

    def get_collection_name(self):
        return "monitor_quote_stocks"

    def add_stock(self, stock):
        collection = self.db[self.get_collection_name()]
        collection.insert({
            "symbol" : stock
        })

    def remove_stock(self, stock):
        collection = self.db[self.get_collection_name()]
        collection.remove({
            "symbol" : stock
        })

    def load_stocks(self):
        collection = self.db[self.get_collection_name()]
        stocks = []
        for t in collection.find():
            stocks.append(t["symbol"])
        return stocks

class FailedTaskModel(object):
    def __init__(self, client):
        self.client = client
        self.db = self.client[self.db_name()]

    def init_db(self):
        self.db.drop_collection(self.get_collection_name())
        collection = self.db[self.get_collection_name()]
        collection.create_index([('time', pymongo.ASCENDING)])

    def db_name(self):
        return "husky"

    def get_collection_name(self):
        return "failed_tasks"

    def add(self, _type, kwargs, reason):
       collection = self.db[self.get_collection_name()]
       collection.insert({
           "type" : _type,
           "kwargs" : kwargs,
           "reason" : reason,
           "time" : datetime.now()
       })

    def get_all(self):
        collection = self.db[self.get_collection_name()]
        return collection.find()