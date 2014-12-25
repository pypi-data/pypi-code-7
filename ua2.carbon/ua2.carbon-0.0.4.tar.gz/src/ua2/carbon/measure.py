import time
import functools

from .stream import send_time

def measure(prefix=None, name=None):
    def _timing(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            metric = name or ('%s.%s' % (func.__module__,
                                         func.__name__))
            if prefix:
                metric = '%s.%s' % (prefix, metric)
            start = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000  # msec
            send_time(metric, duration)
            return result

        return _wrapper

    return _timing
