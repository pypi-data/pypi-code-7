from ddd.domain.valueobject import ValueObject


class Identifier(ValueObject):
    """
    Represents the identifier of a domain entity.
    """
    args = tuple()

    def serialize(self):
        """
        Converts the value-object to a Python dictionary.
        """
        return {x: getattr(self, y) for x, y in self.args}

    def __repr__(self):
        attrs = []
        for name, attname in self.args:
            rpr = '{0}={1}'.format(name, getattr(self, attname).__repr__())
            attrs.append(rpr)
        return "{0}({1})".format(type(self).__name__,
            ', '.join(attrs))