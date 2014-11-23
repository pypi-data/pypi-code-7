import warnings

from cqrs.exceptions import InvalidCommandParameter


RESERVED_ATTRS = ['metadata','handler','accept','serialize','as_dict',
    '_set_parameters', '__getitem__','__iter__','__len__','inspector',
    'as_tuple','__hash__','__eq__','Meta', 'set_result', '_result',
    'get_identity','qualified_name']


class CommandParameter(object):
    empty_values = ['', list(), tuple(), set(), dict(),]
    creation_counter = 0

    def __init__(self, required=True, nullable=False, type=None, empty_values=None,
        default=None, unique=False, primary_key=False):
        self.required = required
        self.type = type or (lambda command, x: x)
        self.nullable = nullable
        if empty_values:
            self.empty_values += list(empty_values)
        CommandParameter.creation_counter += 1
        self.creation_counter = CommandParameter.creation_counter
        self.default = default
        self.unique = False
        self.primary_key = primary_key

    def validate(self, value):
        """
        Validates the input value of a command parameter.
        """

        if value is None and (self.default is not None):
            value = self.default if not callable(self.default)\
                else self.default()

        if value is None and not self.nullable:
            raise InvalidCommandParameter(self.attname,
                "'{0}' is a required parameter".format(self.attname))

        # Assess if the provided value is empty.
        if value is not None:
            is_empty = (hasattr(value, '__len__') and (len(value) == 0))\
                or (value in self.empty_values)
            if is_empty and self.required:
                raise InvalidCommandParameter(self.attname,
                    "'{0}' is a required parameter".format(self.attname))

        return value


    def contribute_to_class(self, cls, name):
        """
        Contributes the :class:`CommandAttribute` to a newly created
        :class:`~cqrs.Command` subclass.

        Args:
            cls: the newly created class.
            name (str): attribute name of the command parameter.
        """
        if name in RESERVED_ATTRS:
            raise ValueError("'{0}' is a reserved name.".format(name))
        self.attname = name
        setattr(cls, name, self)
        cls.__parameters__ += tuple([self])

    def __get__(self, instance, cls):
        return instance._parameters[self.attname] if instance\
            else self


class CommandAttribute(CommandParameter):

    def __init__(self, *args, **kwargs):
        warnings.warn("CommandAttribute is deprecated, use CommandParameter.",
            DeprecationWarning)
        CommandParameter.__init__(self, *args, **kwargs)