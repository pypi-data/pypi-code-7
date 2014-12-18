
class registry(object):
    serializers = dict()

    @classmethod
    def available(cls):
        return cls.serializers.keys()

    @classmethod
    def find(cls, name):
        try:
            return cls.serializers[name]
        except KeyError:
            raise LookupError('No such serializer: %s' % (name,))

    @classmethod
    def register(cls, name, serializer, deserializer):
        cls.serializers[name] = (serializer, deserializer)

    @classmethod
    def unregister(cls, name):
        if name in cls.serializers:
            del cls.serializers[name]


def auto_detect():
    for name, module_name in (['json', 'json'], ['json', 'cJSON'], ['msgpack', 'msgpack']):
        try:
            module = __import__(module_name)
            registry.register(name, module.dumps, module.loads)
        except ImportError:
            pass


auto_detect()
