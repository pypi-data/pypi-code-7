from tornado.web import HTTPError
from app.settings import config
from datetime import datetime

import pytz
import time
import math

if 'timezone' not in config or not config['timezone']:
    raise HTTPError(500, 'Timezone configuration must be set')

_timezone = pytz.timezone(config['timezone'])

def date(format=None, timestamp=None):
    result = None
    if timestamp:
        result = datetime.fromtimestamp(timestamp, _timezone)
    else:
        result = datetime.now(_timezone)
    if format and result:
        return result.strftime(format)
    return result

def microtime(get_as_float=False):
    if get_as_float:
        return time.time()
    else:
        return '%f %d' % math.modf(time.time())