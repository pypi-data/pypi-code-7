from shiftmemory import exceptions, adapter


class Memory():
    """
    Main memory API
    Keeps track of caches, configures and instantiates them on demand and
    provides means to perform operations on caches
    """

    def __init__(self, config=None):
        """
        Creates your memory instance
        Just give it your caches configuration as a dictionary
        """
        self.caches = dict()
        self.config = dict(adapters=dict(), caches=dict())
        if config:
            self.config=config



    def get_cache(self, cache_name):
        """
        Get cache
        Checks if a cache was already created and returns that. Otherwise
        attempts to create a cache from configuration and preserve
        for future use
        """
        if cache_name in self.caches:
            return self.caches[cache_name]

        if not cache_name in self.config['caches']:
            error = 'Cache [{}] is not configured'.format(cache_name)
            raise exceptions.ConfigurationException(error)

        cache_config = self.config['caches'][cache_name]
        adapter_name = cache_config['adapter']

        if not adapter_name in self.config['adapters']:
            error = 'Adapter [{}] is not configured'.format(adapter_name)
            raise exceptions.ConfigurationException(error)

        adapter_config = self.config['adapters'][adapter_name]
        adapter_type = adapter_config['type']
        adapter_class = adapter_type[0].upper() + adapter_type[1:]

        if not hasattr(adapter, adapter_class):
            error = 'Adapter class [{}] is missing'.format(adapter_class)
            raise exceptions.AdapterMissingException(error)


        cls = getattr(adapter, adapter_class)
        cache = cls(
            namespace = cache_name,
            config=adapter_config['config'],
            ttl=cache_config['ttl'],
            )
        self.caches[cache_name] = cache
        return self.caches[cache_name]



    def drop_cache(self, name):
        """
        Drop cache
        Deletes all items in cache by name
        """
        cache = self.get_cache(name)
        if not hasattr(cache, 'delete_all'):
            cls = type(cache)
            error = 'Adapter [{}] can not drop cache by namespace'.format(cls)
            raise exceptions.AdapterFeatureMissingException(error)

        return cache.delete_all()



    def drop_all_caches(self):
        """
        Drop all caches
        Goes through every configured cache and drops all items. Will
        skip certain caches if they do not support drop all feature
        """
        for name in self.config.keys():
            cache = self.get_cache(name)
            if hasattr(cache, 'delete_all'):
                cache.delete_all(name)
        return True



    def optimize_cache(self, name):
        """
        Optimize cache
        gets cache by name and performs optimization if supported
        """
        cache = self.get_cache(name)
        if not hasattr(cache, 'optimize'):
            cls = type(cache)
            error = 'Adapter [{}] can not optimize itself'.format(cls)
            raise exceptions.AdapterFeatureMissingException(error)

        return cache.optimize()



    def optimize_all_caches(self):
        """
        Optimize all caches
        Goes through every configured cache and optimizes. Will
        skip certain caches if they do not support optimization feature
        """
        for name in self.config.keys():
            cache = self.get_cache(name)
            if hasattr(cache, 'optimize'):
                cache.optimize(name)
        return True






