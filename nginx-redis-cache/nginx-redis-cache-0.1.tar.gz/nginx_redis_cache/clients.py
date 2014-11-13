from redis_cache import client


class DefaultClient(client.DefaultClient):
    def pickle(self, value):
        if isinstance(value, basestring):
            return value

        return super(DefaultClient, self).pickle(value)


class HerdClient(client.HerdClient):
    def pickle(self, value):
        if isinstance(value, basestring):
            return value

        return super(HerdClient, self).pickle(value)


class SentinelClient(client.SentinelClient):
    def pickle(self, value):
        if isinstance(value, basestring):
            return value

        return super(SentinelClient, self).pickle(value)


class ShardClient(client.ShardClient):
    def pickle(self, value):
        if isinstance(value, basestring):
            return value

        return super(ShardClient, self).pickle(value)


class SimpleFailoverClient(client.SimpleFailoverClient):
    def pickle(self, value):
        if isinstance(value, basestring):
            return value

        return super(SimpleFailoverClient, self).pickle(value)