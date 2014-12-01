from django.conf import settings
from django.test import TestCase

from smarttest.decorators import no_db_testcase, test_type

from ..backends import RedisRing


@test_type('unit')
@no_db_testcase
class GetCacheTest(TestCase):

    """
    :py:meth:`redisdb.comap.get_cache`
    """

    def test_should_return_cache_by_alias(self):
        from redisdb.compat import get_cache

        client = get_cache('redis_ring')

        self.assertIsInstance(client, RedisRing)

    def test_should_return_cache_by_path(self):
        from redisdb.compat import get_cache

        client = get_cache('redisdb.backends.RedisRing', DB=0)

        self.assertIsInstance(client, RedisRing)

    def test_should_raise_exception_on_nonexisting_backend(self):
        try:
            from redisdb.compat import get_cache, InvalidCacheBackendError
        except ImportError:
            from django.core.cache import get_cache, InvalidCacheBackendError

        self.assertRaises(InvalidCacheBackendError, get_cache, 'redisdb.backends.WrongBackend', DB=0)

    def test_should_raise_exception_on_wrong_backend_path(self):
        try:
            from redisdb.compat import get_cache, InvalidCacheBackendError
        except ImportError:
            from django.core.cache import get_cache, InvalidCacheBackendError

        self.assertRaises(InvalidCacheBackendError, get_cache, 'redisdb.wrong_module.RedisRing', DB=0)

    def test_should_raise_exception_on_wrong_alias(self):
        try:
            from redisdb.compat import get_cache, InvalidCacheBackendError
        except ImportError:
            from django.core.cache import get_cache, InvalidCacheBackendError

        settings.CACHES['wrong_backend'] = {
            'BACKEND': 'redisdb.backends.WrongBackend',
            'DB': '0',
            'LOCATION': [
                'localhost:6379',
                'localhost:6380',
            ]
        }
        try:
            self.assertRaises(InvalidCacheBackendError, get_cache, 'wrong_backend')
        finally:
            del settings.CACHES['wrong_backend']
