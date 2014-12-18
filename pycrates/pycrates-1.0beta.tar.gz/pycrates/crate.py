from .serializers import registry
from .manifest import IField


def create_unpacked(name, fields):
    return type(name, (object,), {'__slots__': fields})


class parsed_manifest(object):
    def __init__(self, manifest_class):
        self.manifest = manifest_class

    @property
    def method(self):
        return getattr(self.manifest, '__method__', 'json')

    @property
    def constructor(self):
        return getattr(self.manifest(), '__construct__', None)

    def get_fields(self):
        return {k: v for k, v in self.manifest.__dict__.items() if isinstance(v, IField)}

    def get_serializer(self):
        return registry.find(self.method)[0]

    def get_deserializer(self):
        return registry.find(self.method)[1]


def pack(obj, manifest):
    serializer = manifest.get_serializer()

    packed = dict()
    for name, field in manifest.get_fields().items():
        packed[name] = field.dumps(getattr(obj, name))

    return serializer(packed)


def unpack(packed, manifest, klass):
    deserializer = manifest.get_deserializer()

    fields = manifest.get_fields()

    obj = create_unpacked('%s__UNPACKED' % (klass.__name__,), fields) if manifest.constructor else klass()

    for name, value in deserializer(packed).items():
        if name in fields:
            setattr(obj, name, fields[name].loads(value))
        else:
            raise ValueError('Unexpected field in data: %s' % (name,))

    if manifest.constructor:
        obj = manifest.constructor(obj)

    return obj


class cratify(object):
    def __init__(self, klass, manifest):
        self.klass = klass
        self.manifest = parsed_manifest(manifest)

    def pack(self, obj):
        if not isinstance(obj, self.klass):
            raise ValueError('object is not type %s' % (self.klass.name,))

        return pack(obj, self.manifest)

    def unpack(self, packed):
        return unpack(packed, self.manifest, self.klass)


class Crate(object):
    def pack(self):
        return pack(self, parsed_manifest(self.__manifest__))

    @classmethod
    def unpack(cls, packed):
        return unpack(packed, parsed_manifest(cls.__manifest__), cls)

