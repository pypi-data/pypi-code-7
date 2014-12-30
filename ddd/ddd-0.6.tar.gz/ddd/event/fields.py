

class Field(object):
    """Represents a data-member of an event type."""
    creation_counter = -1

    def __init__(self, datatype=lambda x: x, name=None):
        """Initialize a new :class:`Field` instance.

        Args:
            datatype: a callable that coerces a value to the desired
                datatype.
            name (str): specifies the field name; if `name` is ``None``,
                it will be equal to :attr:`Field.attname`.
        """
        self.datatype = datatype
        self.name = None
        self.attname = None
        Field.creation_counter += 1
        self.creation_counter = Field.creation_counter 

    def contribute_to_class(self, cls, name):
        """Adds the field to a new event type class."""
        meta = cls.__meta__
        self.attname = name
        if self.name is None:
            self.name = self.attname
        meta.add_field(self)

    def __lt__(self, other):
        return self.creation_counter < other.creation_counter
