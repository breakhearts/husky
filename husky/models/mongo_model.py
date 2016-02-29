from pymongo import MongoClient
from husky.api import nasdaq
import pymongo

def get_mongo_client(host, port):
    client = MongoClient(host, port)
    return client

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
        self.client.drop_database(self.db_name())
        for _type in (nasdaq.REAL_TIME_QUOTE, nasdaq.AFTER_HOUR_QUOTE, nasdaq.PRE_MARKET_QUOTE):
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