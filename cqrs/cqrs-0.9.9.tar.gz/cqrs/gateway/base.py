import abc
import collections
import threading
import random
import sys

class IGateway(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def dispatch(self, command, *args, **kwargs):
        """
        Executes the given command.
        """
        pass

    def put(self, command, *args, **kwargs):
        """Put a command an assess if it can be executed; proceed to
        invoke the command-runner to execute. Returns a :class:`uuid4
        cqrs.Transaction` instance representing the transaction.

        Args:
            command (cqrs.Command): a concrete command implementation.
            **extra_metadata: extra metadata parameters.

        Returns:
            cqrs.Transaction
        """
        self.dispatch(command, *args, **kwargs)


    @abc.abstractmethod
    def dispatch(self, command, *args, **kwargs):
        """Dispatches the command to the command-processing gateway
        backend.

        Args:
            command: the command to dispatch.
        """
        raise NotImplementedError
