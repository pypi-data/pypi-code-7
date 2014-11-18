# define obligatory use of ssl/tls or services modules autoreload
IS_DEVELOPMENT = False

# user session timeout in seconds
SESSION_TIMEOUT = 3600

# max active user sessions (negative means no limit)
MAX_ACTIVE_USER_SESSIONS = -1

# threshold of abuses by host to trigger rejection
MAX_ORIGIN_ABUSE_LEVEL = 10

# reset host abuses count after X seconds
ABUSE_LEVEL_WATCH_PERIOD = 600

# seconds granted to perform login after successfull prelogin
PRELOGIN_GRACE_TIME = 3

# max pending prelogin attempts by user
MAX_PRELOGIN_COUNT = 1

# seconds granted to perform safe call after successfull gen_pad
PAD_GRACE_TIME = 3

# max queued pads by user for the same safe call
MAX_PADS_COUNT = 1

# logging setup
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'console': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },

    'handlers': {
        #'sentry': {
        #    'level': 'ERROR',
        #    'class': 'raven.handlers.logging.SentryHandler',
        #    'dsn': 'https://public:secret@example.com/1',
        #},
        #'graypy': {
        #    'level': 'INFO',
        #    'class': 'graypy.GELFRabbitHandler',
        #    'url': 'amqp://guest:guest@example.com:5672/%2F',
        #},
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },

    'loggers': {
        'fanery': {
            'handlers': ['console', ],  # 'sentry', 'graypy'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
import logging.config
logging.config.dictConfig(LOGGING)

# file upload folder
from tempfile import gettempdir
UPLOAD_DIRPATH = gettempdir()

# jfanery static files folder
from os.path import realpath, normpath, dirname, join
JFANERY_DIRPATH = join(realpath(normpath(dirname(__file__))), 'jfanery')
JFANERY_URLPATH = '/jfanery'
