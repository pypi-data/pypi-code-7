from django.utils.decorators import decorator_from_middleware_with_args
from .middleware import CacheMiddleware


def cache_page(*args, **kwargs):
    """
    Decorator for views that tries getting the page from the cache and
    populates the cache if the page isn't in the cache yet.

    The cache is keyed by the URL and some data from the headers.
    Additionally there is the key prefix that is used to distinguish different
    cache areas in a multi-site setup. You could use the
    sites.get_current_site().domain, for example, as that is unique across a Django
    project.

    Additionally, all headers from the response's Vary header will be taken
    into account on caching -- just like the middleware does.
    """
    # We also add some asserts to give better error messages in case people are
    # using other ways to call cache_page that no longer work.
    if len(args) != 1 or callable(args[0]):
        raise TypeError("cache_page has a single mandatory positional argument: timeout")
    cache_timeout = args[0]
    cache_alias = kwargs.pop('cache', None)
    key_prefix = kwargs.pop('key_prefix', None)
    if kwargs:
        raise TypeError("cache_page has two optional keyword arguments: cache and key_prefix")

    return decorator_from_middleware_with_args(CacheMiddleware)(cache_timeout=cache_timeout,
                                                                cache_alias=cache_alias,
                                                                key_prefix=key_prefix)