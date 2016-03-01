from husky.models.mongo_model import StockQuoteMongoModel, StockQuoteTaskMongoModel, mongo_client

model = StockQuoteMongoModel(mongo_client)
model.init_db()
model = StockQuoteTaskMongoModel(mongo_client)
model.init_db()
for stock in ("baba", "fb", "bidu"):
    model.add_stock(stock)
