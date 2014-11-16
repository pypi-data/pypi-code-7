# -*- coding: utf-8 -*-
from werkzeug.local import LocalProxy
from functools import partial


__settings  = None
__cur_phial = None
__celery    = None


settings      = LocalProxy(partial(lambda: __settings))
current_phial = LocalProxy(partial(lambda: __cur_phial))
celery        = LocalProxy(partial(lambda: __celery))
