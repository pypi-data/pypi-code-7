"""Errors raised by the package."""


class Error(Exception):
    """Base error class."""


class ConfigError(Error):
    """Raised on config error."""


class ContainerError(Error):
    """Raised on container error."""


class VersionError(Error):
    """Raised on version detection failure."""


class TestError(Error):
    """
    Raised on test failure. The object's `exit_code` attribute should contain the exit code of the
    failed test.
    """

    def __init__(self, msg, exit_code=None):
        """Initialize the error. Set the `exit_code` value to the provided param."""
        super(TestError, self).__init__(msg)
        self.exit_code = exit_code
