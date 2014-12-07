from redis import StrictRedis
from shiftmemory import exceptions, times

class Redis:
    """
    Redis adapter
    Implements cache for items under namespaces in a single database. In
    addition each item can be marked by tags and can have optional custom
    expiration. You can then perform fetch by key or remove items by tags or
    namespaces.

    The way it works is that each cached item is stored as redis hash
    consisting of data and tags. Each tag is stored as redis set consisting
    of hash ids for tagged items.

    It is important to notice that expired items won't be removed from
    tags automatically, that is why you can optimize your cache with optimize
    command and there is a simple garbage collection in place.
    """

    def __init__(
        self,
        namespace,
        ttl=60,
        namespace_separator=None,
        optimize_after = '+2 days',
        **config
    ):
        """
        Create adapter
        Instantiates adapter with namespace, default ttl and optional
        connection configuration parameters

        :param namespace:           namespace name
        :param ttl:                 default ttl for all items (default=60)
        :param namespace_separator: string
        :param config:              connection configuration (optional)
        :param optimize_after:      collect garbage after period (None=off)
        :return:                    None
        """
        self.redis = None
        self.config = None

        self.ttl = ttl
        self.namespace = namespace

        self.namespace_separator = '::'
        if namespace_separator:
            self.namespace_separator = namespace_separator

        # key prefixes for items and tags
        self.item_prefix = self.namespace + self.namespace_separator
        self.tag_prefix = self.item_prefix + 'tags' + self.namespace_separator

        # init redis connection
        self.configure(config)

        # collect garbage if it's time
        if optimize_after:
            self.optimize_after = optimize_after
            self.collect_garbage()



    def configure(self, config=None):
        """
        Configure
        Configures an adapter with optional config. If no config provided
        or it misses some settings, defaults will be used.

        :param config:          config dictionary
        :return:                None
        """
        default_config = dict(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

        if config is None: config = dict()
        self.config = dict(list(default_config.items()) + list(config.items()))

        if 'unix_socket_path' in self.config:
            del self.config['host'], self.config['port']


    def get_redis(self):
        """
        Get redis
        Checks if we have a connection and returns that. Otherwise creates
        one from config and preserves for future use

        :return:                redis.client.StrictRedis
        """
        if not self.redis:
            self.redis = StrictRedis(**self.config)

        return self.redis


    # -------------------------------------------------------------------------
    # Keys
    # -------------------------------------------------------------------------

    def get_full_item_key(self, key):
        """
        Get full item keys
        Returns normalized item cache key with a namespace prepended.
        This will be used to store a hash of data and tags

        :param key:             string key
        :return:                string normalized key
        """
        if self.is_full_item_key(key):
            return key

        key = self.item_prefix + key
        return key



    def is_full_item_key(self, key):
        """
        Is full item key?
        Checks if provided key is a full item cache key used for storage. It
        should contain prepended namespace.

        :param key:             string, key to check
        :return:                bool
        """
        return key.startswith(self.item_prefix)



    def get_tag_set_key(self, tag):
        """
        Get tag set key
        Returns tag set key used to store tagged items hash ids

        :param key:             string, tag
        :return:                string, tag set key
        """
        if tag.startswith(self.tag_prefix):
            return tag

        return self.tag_prefix + tag


    # -------------------------------------------------------------------------
    # Caching
    # -------------------------------------------------------------------------


    def check_ttl_support(self):
        """
        Check ttl support
        Checks major redis version to be >2 for ttl support and raises
        feature exception if it's not

        :return:                None
        """
        redis = self.get_redis()
        version = redis.info('server')['redis_version']
        major = int(version.split('.')[0])
        if major < 2:
            error = 'To use TTL you need Redis >= 2.0.0'
            raise exceptions.AdapterFeatureMissingException(error)

        return True



    def exists(self, key):
        """
        Item exists?
        Checks item existence by the given key to return a boolean result

        :param key:             string, item key
        :return:                bool
        """
        key = self.get_full_item_key(key)
        result = self.get_redis().exists(key)
        return result



    def set(self, key, value, *, tags=None, ttl=None, expires_at=None):
        """
        Set item
        Creates or updates and item (hash). Can optionally accept an iterable
        of tags to add to item and either ttl or expiration date for custom
        item expiration, otherwise falls back to default adapter ttl.
        Expiration date accepts various formats, see ttl_from_expiration()
        for more info.

        :param key:             string, cache key
        :param value:           string, data to put
        :param tags:            iterable or None, any tags to add
        :param ttl:             int, optional custom ttl in seconds
        :param expires_at:      optional expiration date (utc)
        :return:                bool
        """

        redis = self.get_redis()

        # data
        key = self.get_full_item_key(key)
        redis.hset(key, 'data', value)

        # expire
        if expires_at: ttl = times.ttl_from_expiration(expires_at)
        if not ttl: ttl = self.ttl
        redis.expire(key, ttl)

        # tag
        if tags:
            self.set_tags(key, list(tags))

        return True



    def add(self, key, value, *, tags=None, ttl=None, expires_at=None):
        """
        Add
        Similar to set item but only saves an item if it does not exist yet.
        Will return false in case in does.

        :param key:             string, cache key
        :param value:           string, data to put
        :param tags:            iterable or None, any tags to add
        :param ttl:             int, optional custom ttl in seconds
        :param expires_at:      optional expiration date (utc)
        :return:                bool
        """
        if self.exists(key):
            return False
        return self.set(key, value, tags=tags, ttl=ttl, expires_at=expires_at)



    def get(self, key=None):
        """
        Get
        Get single item by key.

        :param key:             item key
        :return:                string or None
        """
        key = self.get_full_item_key(key)
        return self.get_redis().hget(key, 'data')



    def delete(self, key=None, *, tags=None, disjunction=False):
        """
        Delete
        Removes an item by key or several items marked with tags.
        If disjunction is False (default) all tags must match
        otherwise any tag can match.

        :param key:             int, item key
        :param tags:            Iterable, tags to fetch by
        :return:                bool
        """
        redis = self.get_redis()

        if key:
            key = self.get_full_item_key(key)
            return redis.delete(key)


        # disjunction or single tag
        if disjunction or len(tags) <= 1:
            result = True
            for tag in tags:
                tagged = self.get_tagged_items(tag)
                if not tagged:
                    continue

                for item_key in tagged:
                    result += self.delete(item_key)

            return result

        # without disjunction (all match)
        tags_keys = [self.get_tag_set_key(tag) for tag in tags]
        delete_us = redis.sinter(tags_keys)
        if not delete_us:
            return False

        multi = redis.pipeline()
        for item_key in delete_us:
            multi.delete(item_key)

        result = multi.execute()
        return result


    def delete_all(self):
        """
        Delete all
        Removes all cached item stored under current namespace

        :return:                bool
        """
        redis = self.get_redis()
        ns = self.item_prefix + '*'
        keys = redis.keys(ns)
        return redis.delete(*keys)



    def set_tags(self, item_key, tags):
        """
        Set tags
        Sets an iterable of tags to an item and creates or updates tag set
        for each tag with item key.

        :param item_key:        string, item cache key
        :param tags:            Iterable, tags to set
        :return:                bool
        """
        key = self.get_full_item_key(item_key)
        if not self.exists(key):
            return False

        # remove tags?
        if not tags:
            #self.remove_tags(item_key)
            raise NotImplementedError

        redis = self.get_redis()

        # set tags to item
        tag_string = ','.join(tags)
        result = redis.hset(key, 'tags', tag_string)
        if not result:
            return False


        # add item key to tags
        for tag in tags:
            tag_key = self.get_tag_set_key(tag)
            result = redis.sadd(tag_key, key)
            if not result:
                return False

        return True


    def get_tagged_items(self, tag):
        """
        Get tagged items
        Returns a ist of item keys marked with the given tag.

        :param tag:             string, tag
        :return:                list
        """
        key = self.get_tag_set_key(tag)
        result = self.get_redis().smembers(key)
        return result


    def get_item_tags(self, key):
        """
        Get item tags
        Returns a list of items tags by item key

        :param key:             string, item key
        :return:                list | None
        """
        key = self.get_full_item_key(key)
        tag_string = self.get_redis().hget(key, 'tags')
        if not tag_string:
            return

        return tag_string.split(',')




    # -------------------------------------------------------------------------
    # Optimizing
    # -------------------------------------------------------------------------

    def optimize(self):
        """
        Optimize
        Optimizes redis database by walking each tag and ensuring items exist,
        then walking each item end ensuring all tags exist.

        :return:                bool
        """
        redis = self.get_redis()
        keys = redis.keys(self.item_prefix + '*')

        for key in keys:
            is_tag = key.startswith(self.tag_prefix)

            # optimize tag
            if is_tag:
                items = self.get_tagged_items(key)
                for item in items:
                    # clear missing items from sets
                    if not redis.exists(item):
                        redis.srem(key, item)

                    # clear empty sets
                    if redis.scard(key) == 0:
                        redis.delete(key)
                        continue

            # optimize item
            else:
                tags = self.get_item_tags(key)
                if not tags:
                    continue

                updated_tags = []
                for tag in tags:
                    # remove missing tags from items
                    tagged_items = self.get_tagged_items(tag)
                    if tagged_items:
                        updated_tags.append(tag)

                redis.hset(key, 'tags', updated_tags)

        return True


    def collect_garbage(self):
        """
        Collect garbage
        Checks previous garbage collection timestamp and performs optimization
        if its time to do so. You should consider lower optimization
        timeout than default under load.

        :return:                None
        """
        from shiftmemory import times
        from datetime import datetime

        timeout = self.optimize_after
        key = self.get_full_item_key('__gc')

        next_gc = self.get(key)

        # first run?
        if not next_gc:
            next_gc = times.expires_to_timestamp(timeout)
            self.set(key, next_gc)
            return False

        # not yet?
        next_gc = int(next_gc)
        now = int(datetime.utcnow().timestamp())
        if now < next_gc:
            return False

        # optimize now
        self.optimize()
        next_gc = times.expires_to_timestamp(timeout)
        self.set(key, next_gc)
        return True


















