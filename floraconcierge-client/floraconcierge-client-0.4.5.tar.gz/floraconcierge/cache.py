import hashlib
import pickle
from threading import currentThread

from django.core.cache.backends.locmem import LocMemCache

from floraconcierge.errors import MiddlewareError


_request_cache = {}
_installed_middleware = False


def get_request_cache():
    try:
        return _request_cache[currentThread()]
    except KeyError:
        raise MiddlewareError('floraconcierge.middleware.RequestCacheMiddleware not loaded')


def new_request_cache(cachecls):
    _request_cache[currentThread()] = cache = cachecls()

    return cache


def cached(function):
    def _make_key(args, kwargs):
        data = [function.__name__, args[0].__class__.__name__, pickle.dumps((args[1:], kwargs))]

        return hashlib.md5("%".join(data)).hexdigest()

    def inner(*args, **kwargs):
        key = _make_key(args, kwargs)
        obj = args[0]

        if key in obj:
            return obj.get(key)
        else:
            result = function(*args, **kwargs)
            obj.add(key, result)

            return result

    return inner


class RequestCache(LocMemCache):
    def __init__(self):
        name = 'requestcache@%i' % hash(currentThread())
        super(RequestCache, self).__init__(name, {})