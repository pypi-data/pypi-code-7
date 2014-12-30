import collections

from ddd.domain.entity.meta import EntityMeta


class Entity(metaclass=EntityMeta):

    def __init__(self, *args, **kwargs):
        for p in self.__properties__.values():
            value = kwargs.get(p.name)
            if value is None and p.required:
                raise ValueError
            if value is None and p.default:
                value = p.default(self) if callable(p.default)\
                    else p.default
            p.set(self, value)


    def get_identity(self):
        """Return a :class:`namedtuple` representing the identity
        of the domain object."""
        raise NotImplementedError

    def accept_visitor(self, visitor):
        """
        Accepts a visitor instance. :class:`~ddd.domain.Visitor`
        instances may access internal attributes of the domain entity.

        Args:
            visitor (ddd.domain.Visitor): a concrete visitor
                implementation.

        Returns:
            None
        """
        return visitor.visit(self)

    def __hash__(self):
        ident = self.get_identity()
        if ident is None:
            raise TypeError("Entity must have an identity to be hashable.")
        assert all([isinstance(x, collections.Hashable) for x in ident]),\
            "All members of the identity should be hashable."
        return hash(ident)

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, "Object")
