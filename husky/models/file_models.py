from husky.utils import utility
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

    def get_file_name(self, _type, stock, date):
        return os.path.join(self.root(), "{0}/{1}/{2}".format(_type, stock, date))

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
