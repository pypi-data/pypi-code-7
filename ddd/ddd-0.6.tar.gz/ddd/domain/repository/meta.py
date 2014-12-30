import abc

from libtng import six
from ddd.domain.repository.cache import RepositoryCache


class RepositoryMeta(abc.ABCMeta):

    def __new__(cls, name, bases, attrs):
        super_new = super(RepositoryMeta, cls).__new__

        # six.withmetaclass() inserts an extra class called 'NewBase' in the
        # inheritance tree: Repository -> NewBase -> object. But the initialization
        # should be executed only once for a given model class.

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super_new(cls, name, bases, attrs)

        # Also ensure initialization is only performed for subclasses of Repository
        # (excluding Repository class itself).
        parents = [b for b in bases if isinstance(b, RepositoryMeta) and
                not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))]
        if not parents:
            return super_new(cls, name, bases, attrs)
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})

        # Add all attributes declared on the class to the newly
        # created type.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        # Create the object cache
        new_class.add_to_class('_cache', RepositoryCache())

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)