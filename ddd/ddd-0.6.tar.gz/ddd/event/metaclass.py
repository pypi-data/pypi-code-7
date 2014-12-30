from ddd.event.options import Options
from ddd.event.fields import Field


#: A list of reserver attribute names
RESERVED_ATTRS = ['__meta__']


class EventMetaclass(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(EventMetaclass, cls).__new__

        # Also ensure initialization is only performed for subclasses of Entity
        # (excluding Entity class itself).
        parents = [b for b in bases if isinstance(b, EventMetaclass)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        module = attrs.pop('__module__')
        meta = attrs.pop('Meta', None)
        new_class = super_new(cls, name, bases, {
            '__module__': module,
            '__properties__': {}
        })

        # Add the inner metaclass to the new class.
        new_class.add_to_class('__meta__', Options(meta))

        # Add all attributes to the new class.
        fields = []
        for attname, value in attrs.items():
            if attname in RESERVED_ATTRS:
                raise ValueError("`{0}` is a reserved name".format(name))
            if isinstance(value, Field):
                fields.append([attname, value])
                continue
            new_class.add_to_class(attname, value)

        # Sort the fields and add them to the class in order.
        fields = sorted(fields, key=lambda x: x[1])
        for attname, value in fields:
            new_class.add_to_class(attname, value)

        # The new class is ready now, so call prepare() on the Options
        # class to do all post-creation tasks.
        new_class.__meta__.prepare()

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

