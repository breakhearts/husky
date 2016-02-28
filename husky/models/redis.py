from __future__ import absolute_import
import redis

class RedisClient(object):
    def __init__(self, host, port, db):
        self.host = host
        self.post = port
        self.db = db
        self.connect()

    def connect(self):
        self.r = redis.StrictRedis(self.host, self.post, self.db)

class QuoteModel(object):
    def __init__(self):
        pass

    def
