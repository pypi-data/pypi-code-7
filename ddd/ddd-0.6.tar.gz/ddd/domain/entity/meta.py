from collections import OrderedDict
from collections import namedtuple

from ddd.domain.entity.property import Property


class EntityMeta(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(EntityMeta, cls).__new__

        # six.withmetaclass() inserts an extra class called 'NewBase' in the
        # inheritance tree: Entity -> NewBase -> object. But the initialization
        # should be executed only once for a given model class.

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super_new(cls, name, bases, attrs)

        # Also ensure initialization is only performed for subclasses of Entity
        # (excluding Entity class itself).
        parents = [b for b in bases if isinstance(b, EntityMeta) and
                not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))]
        if not parents:
            return super_new(cls, name, bases, attrs)
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module,
            '__properties__': OrderedDict()})

        # Create exceptions
        exc_name = 'DoesNotExist'
        attrs[exc_name] = type(exc_name, (LookupError,), {})

        # Add all attributes declared on the class to the newly
        # created type.
        properties = []
        for obj_name, obj in attrs.items():
            if isinstance(obj, Property):
                properties.append([obj_name, obj])
                continue
            new_class.add_to_class(obj_name, obj)

        # Create a namedtuple serving as data transfer object.
        new_class.add_to_class('_tuple_cls',
            namedtuple(name, [x[0] for x in properties]))

        # Add properties in sorted order.
        for name, prop in sorted(properties, key=lambda x: x[1].creation_counter):
            new_class.add_to_class(name, prop)

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)
