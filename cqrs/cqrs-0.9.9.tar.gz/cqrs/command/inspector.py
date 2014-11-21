


class CommandInspector(object):
    """
    Inspects and provides access to the internal state
    of :class:`~cqrs.Command` instances.
    """

    def getattr(self, command, attname):
        """Returns the command parameter."""
        return command._parameters[attname]

    def get_parameters(self, command):
        """
        Returns a :class:`tuple` of :class:`~cqrs.CommandParameter`
        instances specifying the parameters required by the command.
        """
        return command.__parameters__

    def as_dict(self, command):
        """
        Returns the parameters of a command as a Python dictionary,
        so that the output of :class:`CommandInspector.as_dict()`
        can be used to reinstantiate the object.
        """
        return {x.attname: self.getattr(command, x.attname)
            for x in command.__parameters__}

    def get_import_path(self, cls):
        """
        Returns the full dotted path of a class.
        """
        return cls.__module__ + '.' + cls.__name__

    def hash(self, command):
        """Implement the __hash__ method of a command."""
        return hash(command.as_tuple())

    def get_ident_attrs(self, command):
        return filter(lambda x: x.primary_key,
            self.get_parameters(command))