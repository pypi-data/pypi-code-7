import time
import functools

from .stream import send_time

def measure(prefix, name=None):
    """Decorator for send stats to graphite"""
    def _timing(func):

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            _name = name or ('%s.%s' % (func.__module__,
                                        func.__name__))
            metric = '%s.%s' % (prefix, _name)
            start = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000  # msec

            send_time(metric, duration)
            return result

        return _wrapper

    return _timing
