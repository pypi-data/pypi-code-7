import threading


class localcache(threading.local):

    @property
    def cache(self):
        if not hasattr(self, '_cache'):
            self._cache = {}
        return self._cache


class RepositoryCache(object):
    """Caches domain entities in the local thread."""

    def __init__(self):
        self.__local = localcache()

    def set(self, identifier, instance):
        """Caches a domain entity."""
        self.__local.cache[identifier] = instance

    def get(self, identifier):
        """Get a domain entity by it's identifier."""
        return self.__local.cache.get(identifier)