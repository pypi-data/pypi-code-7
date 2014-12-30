

class Property(object):
    creation_counter = 0

    def __init__(self, type=None, default=None, required=False, ident=False):
        self.object_type = type
        self.default = default
        self.required = required
        self.private_attname = None
        self.name = None
        self.creation_counter = Property.creation_counter
        self.creation_counter += 1
        self.ident = ident

    def get(self, instance):
        return getattr(instance, self.private_attname)

    def set(self, instance, value):
        setattr(instance, self.private_attname, value)

    def contribute_to_class(self, cls, attname):
        """
        Adds the property to it's parent class.
        """
        self.name = attname
        self.private_attname = '_' + attname.strip('_')
        cls.__properties__[self.name] = self
