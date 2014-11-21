

class MissingCommandHandler(ImportError):
    pass


class UnknownCommand(Exception):
    pass


class InvalidRequestData(Exception):
    pass


class UnprocessableCommandException(Exception):
    """
    Base class for exceptions raised when a command could
    not be processed.
    """
    http_status_code = None

    def __init__(self, http_status_code=None, *args, **kwargs):
        if http_status_code is not None:
            self.http_status_code = http_status_code

    def get_http_status_code(self):
        """
        Returns the HTTP status code associated with the exception.
        """
        return self.http_status_code or 500


class CommandDeserializationError(UnprocessableCommandException):
    """Raised when a command could not be deserialized by the gateway."""
    http_status_code = 422


class InvalidCommandParameter(UnprocessableCommandException):
    """
    Raised when a command could not be instatiated because of an invalid
    parameter. Mau be translated to a 422 UNPROCESSABLE ENTITY response.
    """
    http_status_code = 422


class InvalidCommandParameters(UnprocessableCommandException):
    """
    Raised when a command could not be instatiated because of invalid
    parameters. May be translated to a 422 UNPROCESSABLE ENTITY response.
    """
    http_status_code = 422

    def __init__(self, *args, **kwargs):
        self.invalid_parameters = kwargs.pop('parameters', [])
        UnprocessableCommandException.__init__(self, *args, **kwargs)


class GatewayNotResponding(UnprocessableCommandException):
    """
    Raised when a (remote) gateway is not responding. In a HTTP context
    this should translate to a 502 response; if the server does not want to
    disclose this information, use 503 instead.
    """
    http_status_code = 503


class GatewayRejectedCommand(UnprocessableCommandException):
    """
    Raised when a command was valid but the gateway rejected it. May be
    translated to a 422 HTTP response.
    """
    http_status_code = 422


class DuplicateCommand(UnprocessableCommandException):
    """
    Raised when an identical command is dispatched that should be
    unique within a certain timeframe; e.g. if the command
    ``RegisterSystemOperator('foo', 'mypassword')`` should be unique
    within an arbitrary timeframe. May be translated to a 409 CONFLICT
    response.
    """
    http_status_code = 409
