from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, get_cache
from django.middleware.cache import FetchFromCacheMiddleware
from django.middleware.cache import UpdateCacheMiddleware as OrigUpdateCacheMiddleware
from django.utils.cache import get_max_age
from django.utils.encoding import force_bytes
import hashlib
import warnings
import re


class UpdateCacheMiddleware(OrigUpdateCacheMiddleware):
    def process_response(self, request, response):
        """Sets the cache, if needed."""
        if response.streaming or response.status_code != 200:
            return response
        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length.
        timeout = get_max_age(response)
        if timeout is None:
            timeout = self.cache_timeout
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            return response
        # patch_response_headers(response, timeout)
        if timeout:
            cache_key = hashlib.md5(force_bytes(re.sub(r'^https?://', '', request.build_absolute_uri()))).hexdigest()

            if hasattr(response, 'render') and callable(response.render):
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r, timeout)
                )
            else:
                self.cache.set(cache_key, response.content, timeout)
        return response


class CacheMiddleware(UpdateCacheMiddleware, FetchFromCacheMiddleware):
    """
    Cache middleware that provides basic behavior for many simple sites.

    Also used as the hook point for the cache decorator, which is generated
    using the decorator-from-middleware utility.
    """

    def __init__(self, cache_timeout=None, cache_anonymous_only=None, **kwargs):
        # We need to differentiate between "provided, but using default value",
        # and "not provided". If the value is provided using a default, then
        # we fall back to system defaults. If it is not provided at all,
        # we need to use middleware defaults.

        cache_kwargs = {}

        try:
            self.key_prefix = kwargs['key_prefix']
            if self.key_prefix is not None:
                cache_kwargs['KEY_PREFIX'] = self.key_prefix
            else:
                self.key_prefix = ''
        except KeyError:
            self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
            cache_kwargs['KEY_PREFIX'] = self.key_prefix

        try:
            self.cache_alias = kwargs['cache_alias']
            if self.cache_alias is None:
                self.cache_alias = DEFAULT_CACHE_ALIAS
            if cache_timeout is not None:
                cache_kwargs['TIMEOUT'] = cache_timeout
        except KeyError:
            self.cache_alias = settings.CACHE_MIDDLEWARE_ALIAS
            if cache_timeout is None:
                cache_kwargs['TIMEOUT'] = settings.CACHE_MIDDLEWARE_SECONDS
            else:
                cache_kwargs['TIMEOUT'] = cache_timeout

        if cache_anonymous_only is None:
            self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)
        else:
            self.cache_anonymous_only = cache_anonymous_only

        if self.cache_anonymous_only:
            msg = "CACHE_MIDDLEWARE_ANONYMOUS_ONLY has been deprecated and will be removed in Django 1.8."
            warnings.warn(msg, PendingDeprecationWarning, stacklevel=1)

        self.cache = get_cache(self.cache_alias, **cache_kwargs)
        self.cache_timeout = self.cache.default_timeout