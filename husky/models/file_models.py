from husky.utils import utility
from husky.api import nasdaq
import json
import os


class StockQuoteFileModel(object):
    """
    save/load quote data into file system
    """
    def __init__(self, path):
        self._root = path

    def root(self):
        return self._root

    def get_collection_name(self, type):
        if type == nasdaq.REAL_TIME_QUOTE:
            return "real_time_quote"
        elif type == nasdaq.AFTER_HOUR_QUOTE:
            return "after_hour_quote"
        elif type == nasdaq.PRE_MARKET_QUOTE:
            return "pre_market_quote"
        return ""

    def get_file_name(self, _type, stock, date):
        return os.path.join(self.root(), "{0}/{1}/{2}".format(self.get_collection_name(_type), stock, date))

    def save_stock_quote(self, _type, stock, date, data):
        fname = self.get_file_name(_type, stock, date)
        utility.wise_mk_dir_for_file(fname)
        obj = {
            "stock": stock,
            "date": date,
            "data": data
        }
        with open(fname, "wb") as f:
            f.write(json.dumps(obj))

    def load_stock_quote(self, _type, stock, date):
        fname = self.get_file_name(_type, stock, date)
        if not os.path.exists(fname):
            return None
        with open(fname, "rb") as f:
            t = json.loads(f.read())
            return t

    def remove_stock(self, _type, stock, date):
        fname = self.get_file_name(_type, stock, date)
        if not os.path.exists(fname):
            return
        os.remove(fname)
