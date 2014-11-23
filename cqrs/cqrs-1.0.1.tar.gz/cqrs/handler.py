import abc


class CommandHandler(metaclass=abc.ABCMeta):
    """
    Base class for command handlers. Subclasses must override
    the :meth:`CommandHandler.handle` method.
    """

    @abc.abstractmethod
    def handle(self, command, *args, **kwargs):
        """
        Execute the command. Receives the command and additional
        parameters passed to the gateway.
        """
        pass

    def run_command(self, command, func, *args, **kwargs):
        # Private method to allow setting up a specific command
        # execution context.
        return func(command, *args, **kwargs)
