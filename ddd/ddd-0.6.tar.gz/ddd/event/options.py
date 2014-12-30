from collections import namedtuple


class Options(object):
    """Specifies options for an event type."""

    def __init__(self, meta):
        self.meta = meta
        self.fields = []
        self.dto_type = None
        self.event_type = None

    def contribute_to_class(self, cls, name):
        meta = self.meta
        delattr(self, 'meta') 
    
        # Get the verbose name from the inner meta class, or guess it from
        # the event class name.
        self.verbose_name = getattr(meta, 'verbose_name', cls.__name__)
        self.verbose_name_plural = getattr(meta, 'verbose_name_plural',
            cls.__name__ + 's')


        # Finally, add the Options object to the event type and the event type
        # to the Options object.
        setattr(cls, name, self)
        self.event_type = cls

    def add_field(self, field):
        """Adds a field to the event type."""
        self.fields.append(field)

    def get_fields(self):
        """Return a list containing all fields declared on the event type."""
        return self.fields

    def prepare(self):
        """Perform all post-creation tasks."""

        # Create the data transfer object.
        name = self.event_type.__name__ + 'DataTransferObject'
        attnames = ['timestamp'] + [x.name for x in self.fields]
        self.dto_type = namedtuple(name, attnames)        





