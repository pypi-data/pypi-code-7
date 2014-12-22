
class ApeError(Exception):
    """
    The Base Exception for code in this package
    """


class ConfigurationError(ApeError):
    """
    An error to raise if a component or part is mis-configured.
    """


class DontCatchError(ApeError):
    """
    An exception to put in Operations so they don't catch ApeErrors
    """
