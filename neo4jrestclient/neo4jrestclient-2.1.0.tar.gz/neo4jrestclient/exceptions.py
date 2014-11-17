# -*- coding: utf-8 -*-


class StatusException(IOError):
    """
    Create an Error Response.
    """

    def __init__(self, value, result=None):
        self.value = value
        self.responses = {
            100: ('Continue',
                  'Request received, please continue'),
            101: ('Switching Protocols',
                  'Switching to new protocol; obey Upgrade header'),
            200: ('OK',
                  'Request fulfilled, document follows'),
            201: ('Created',
                  'Document created, URL follows'),
            202: ('Accepted',
                  'Request accepted, processing continues off-line'),
            203: ('Non-Authoritative Information',
                  'Request fulfilled from cache'),
            204: ('No Content',
                  'Request fulfilled, nothing follows'),
            205: ('Reset Content',
                  'Clear input form for further input.'),
            206: ('Partial Content',
                  'Partial content follows.'),
            300: ('Multiple Choices',
                  'Object has several resources -- see URI list'),
            301: ('Moved Permanently',
                  'Object moved permanently -- see URI list'),
            302: ('Found',
                  'Object moved temporarily -- see URI list'),
            303: ('See Other',
                  'Object moved -- see Method and URL list'),
            304: ('Not Modified',
                  'Document has not changed since given time'),
            305: ('Use Proxy',
                  'You must use proxy specified in Location to access this '
                  'resource.'),
            307: ('Temporary Redirect',
                  'Object moved temporarily -- see URI list'),
            400: ('Bad Request',
                  'Bad request syntax or unsupported method'),
            401: ('Unauthorized',
                  'No permission -- see authorization schemes'),
            402: ('Payment Required',
                  'No payment -- see charging schemes'),
            403: ('Forbidden',
                  'Request forbidden -- authorization will not help'),
            404: ('Not Found',
                  'Nothing matches the given URI'),
            405: ('Method Not Allowed',
                  'Specified method is invalid for this server.'),
            406: ('Not Acceptable',
                  'URI not available in preferred format.'),
            407: ('Proxy Authentication Required',
                  'You must authenticate with '
                  'this proxy before proceeding.'),
            408: ('Request Timeout',
                  'Request timed out; try again later.'),
            409: ('Conflict',
                  'Request conflict.'),
            410: ('Gone',
                  'URI no longer exists and has been permanently removed.'),
            411: ('Length Required',
                  'Client must specify Content-Length.'),
            412: ('Precondition Failed',
                  'Precondition in headers is false.'),
            413: ('Request Entity Too Large',
                  'Entity is too large.'),
            414: ('Request-URI Too Long',
                  'URI is too long.'),
            415: ('Unsupported Media Type',
                  'Entity body in unsupported format.'),
            416: ('Requested Range Not Satisfiable',
                  'Cannot satisfy request range.'),
            417: ('Expectation Failed',
                  'Expect condition could not be satisfied.'),
            418: ('I\'m a teapot',
                  'Is the server running?'),
            500: ('Internal Server Error',
                  'Server got itself in trouble'),
            501: ('Not Implemented',
                  'Server does not support this operation'),
            502: ('Bad Gateway',
                  'Invalid responses from another server/proxy.'),
            503: ('Service Unavailable',
                  'The server cannot process the request due to a high load'),
            504: ('Gateway Timeout',
                  'The gateway server did not receive a timely response'),
            505: ('HTTP Version Not Supported',
                  'Cannot fulfill request.'),
        }
        if result:
            self.result = "\n%s" % result
        else:
            self.result = None  # pedantic, but needed for __str__()

    def __str__(self):
        return u"Code [%s]: %s. %s.%s" % (self.value,
                                          self.responses[self.value][0],
                                          self.responses[self.value][1],
                                          self.result)

    def __unicode__(self):
        return self.__str__()


class TransactionException(StatusException):

    def __init__(self, value=None, message=None):
        if message is None:
            message = "Element not found"
        super(TransactionException, self).__init__(value, message)


class NotFoundError(StatusException):

    def __init__(self, value=None, result=None):
        if not value:
            value = 404
        if not result:
            result = "Node, relationship or property not found"
        super(NotFoundError, self).__init__(value, result)
