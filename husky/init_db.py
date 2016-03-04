from husky.models.mongo_model import StockQuoteMongoModel, StockQuoteTaskMongoModel, StockHistoryMongoModel, mongo_client

model = StockQuoteMongoModel(mongo_client)
model.init_db()
model = StockQuoteTaskMongoModel(mongo_client)
model.init_db()
stocks = (
    'aapl',
    'goog',
    'amzn',
    'fb',
    'baba',
    'jd',
    'bidu',
    'ntes',
    'twtr',
    'qihu',
    'lc',
    'sfun',
    'vips',
    'pypl',
    'wb',
    'sina',
    'sohu',
    'tour',
    'bita',
    'cmcm'
)
for stock in stocks:
    model.add_stock(stock)
model = StockHistoryMongoModel(mongo_client)
model.init_db()
