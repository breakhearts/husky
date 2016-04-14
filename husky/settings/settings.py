import os
from husky.utils import utility
from logging.config import dictConfig


LOG_ROOT = os.path.abspath(os.path.dirname(__file__) + "../../../logs")
utility.wise_mk_dir(LOG_ROOT)

DEBUG = False

LOG_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'normal': {
                'format': '[%(asctime)s]%(levelname)s,%(funcName)s,%(lineno)d,%(message)s'
            },
        },
    'handlers': {
        'console': {
            'formatter': 'normal',
            'class': 'logging.StreamHandler',
            'level': 'DEBUG'
        },
        'exception': {
            'formatter': 'normal',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': "ERROR",
            'filename': os.path.join(LOG_ROOT, "exception"),
            'when': "D",
            'interval': 1
        },
        'husky.tasks.spider_tasks': {
            'formatter': 'normal',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': "DEBUG",
            'filename': os.path.join(LOG_ROOT, "husky.tasks.spider_tasks.log"),
            'when': "D",
            'interval': 1
        },
        'husky.tasks.stock_quote_tasks': {
            'formatter': 'normal',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': "DEBUG",
            'filename': os.path.join(LOG_ROOT, "husky.tasks.stock_quote_tasks.log"),
            'when': "D",
            'interval': 1
        },
        'husky.tasks.stock_history_tasks': {
            'formatter': 'normal',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': "DEBUG",
            'filename': os.path.join(LOG_ROOT, "husky.spiders.stock_history_tasks.log"),
            'when': "D",
            'interval': 1
        }
    },
    'loggers': {
        'husky.tasks.spider_tasks': {
            'handlers': ['husky.tasks.spider_tasks'],
            'level': 'DEBUG',
            'propagate': True
        },
        'husky.tasks.stock_quote_tasks': {
            'handlers': ['husky.tasks.stock_quote_tasks'],
            'level': 'DEBUG',
            'propagate': True
        },
        'husky.tasks.stock_history_tasks': {
            'handlers': ['husky.tasks.stock_history_tasks'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

dictConfig(LOG_SETTINGS)

PROXY_POOL_SERVER_HOST = "192.168.1.100"
PROXY_POOL_LISTEN_PORT = 9000

# stock spider settings
STOCK_SPIDER_USE_PROXY = True
STOCK_SPIDER_TASK_TIMEOUT = 5
STOCK_SPIDER_PAGE_TIMEOUT = STOCK_SPIDER_TASK_TIMEOUT * 10
STOCK_SPIDER_MAX_RETRY = 10

# redis config
REDIS_HOST = "192.168.1.100"
REDIS_PORT = "6379"
REDIS_DB = 0

# mongo config
MONGO_HOST = "192.168.1.100"
MONGO_PORT = 27017

# expires
STOCK_QUOTE_EXPIRES = 60 * 60 * 24
STOCK_HISTORY_EXPIRES = 60 * 60 * 24

STOCK_QUOTE_ROOT = os.path.abspath(os.path.dirname(__file__) + "../../../data/stock_quotes")