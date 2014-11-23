import collections

from cqrs.command.attribute import CommandAttribute as CommandParameter


class CommandMeta(type(collections.Mapping)):

    def __new__(cls, name, bases, attrs):
        super_new = super(CommandMeta, cls).__new__

        # six.withmetaclass() inserts an extra class called 'NewBase' in the
        # inheritance tree: Entity -> NewBase -> object. But the initialization
        # should be executed only once for a given model class.

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super_new(cls, name, bases, attrs)

        # Also ensure initialization is only performed for subclasses of Entity
        # (excluding Entity class itself).
        parents = [b for b in bases if isinstance(b, CommandMeta) and
                not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))]
        if not parents:
            return super_new(cls, name, bases, attrs)
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module,
            '__parameters__': tuple()})

        # Add all attributes to the new class.
        for attname, value in attrs.items():
            new_class.add_to_class(attname, value)

        attnames = map(lambda x: x.attname, new_class.__parameters__)
        new_class.add_to_class('tuple_type', collections.namedtuple(
            name + 'Tuple', attnames))
        new_class.__parameters__ = sorted(new_class.__parameters__,
            key=lambda x: x.creation_counter)
        new_class.__parameters__ = tuple(new_class.__parameters__)

        # Set qualified name
        new_class.qualified_name = module + '.' + name

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)
