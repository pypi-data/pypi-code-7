import abc
import collections
import uuid
import datetime

from cqrs.command.inspector import CommandInspector
from cqrs.command.meta import CommandMeta
from cqrs.exceptions import InvalidCommandParameters
from cqrs.exceptions import InvalidCommandParameter
from cqrs.const import PENDING

__all__ = ['Command']


isoformat = lambda x: datetime.datetime.strptime("%Y-%m-%d %H:%M:%S.%f")
datetime_from_string = lambda x: isoformat(x) if (x is not None) else None


class Command(metaclass=CommandMeta):
    """
    Describes a destructive command on a certain part of a system.
    """

    @property
    def metadata(self):
        return self._metadata

    @property
    def inspector(self):
        return self._inspector

    def __init__(self, *args, **kwargs):
        self._inspector = CommandInspector()
        params = {}
        errors = []
        for param in self._inspector.get_parameters(self):
            value = kwargs.get(param.attname)
            try:
                value = param.validate(value)
                params[param.attname] = value
            except InvalidCommandParameter as e:
                errors.append(e)
        if errors:
            raise InvalidCommandParameters(parameters=errors)
        self._set_parameters(params)
        self._result = None

    @classmethod
    def handler(cls, handler_class):
        """
        Class-decorator to use on a :class:`~cqrs.CommandHandler`
        implementation to register it for `cls`.
        """
        handler_class.command_type = cls
        cls.handler = handler_class
        return handler_class

    def as_dict(self):
        """Project the command as a dictionary."""
        return self.inspector.as_dict(self)

    def _set_parameters(self, params):
        self._parameters = {}
        for param in self._inspector.get_parameters(self):
            self._parameters[param.attname] = params.pop(param.attname)

    def __getitem__(self, key):
        if key not in self._attributes:
            raise KeyError(key)
        return getattr(self, key)

    def __iter__(self):
        return self.as_dict().__iter__()

    def __len__(self):
        return len(self.as_dict().keys())

    def __hash__(self):
        return self.inspector.hash(self)

    def __eq__(self, other):
        return hash(self) == hash(other)
