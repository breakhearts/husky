import os
from husky.utils import utility
LOG_ROOT = os.path.abspath(os.path.dirname(__file__) + "../../../logs")
utility.wise_mk_dir(LOG_ROOT)

DEBUG = True

LOG_SETTINGS = {
    'version' : 1,
    'disable_existing_loggers': False,
    'handlers' : {
        "husky.asynctasks.tasks" : {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level' : "INFO",
            'filename': os.path.join(LOG_ROOT, "husky.asynctasks.tasks.log"),
            'when' : "D",
            'interval' : 1
        }
    },
    'loggers' : {
        "husky.asynctasks.tasks" : {
            'handlers' : ["husky.asynctasks.tasks"]
        }
    }
}

PROXY_POOL_SERVER_HOST = "localhost"
PROXY_POOL_LISTEN_PORT = 9000