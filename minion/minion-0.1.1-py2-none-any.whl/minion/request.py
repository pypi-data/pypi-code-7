from __future__ import absolute_import
from characteristic import Attribute, attributes
from twisted.internet.defer import Deferred
from werkzeug.http import HTTP_STATUS_CODES as HTTP_STATUS_PHRASES

from minion.compat import iteritems
from minion.http import Headers, MutableHeaders


HTTP_STATUS_CODES = dict(
    (code, "{0} {1}".format(code, phrase))
    for code, phrase in iteritems(HTTP_STATUS_PHRASES)
)


class Responder(object):
    """
    A responder represents a pending HTTP response for a corresponding request.

    """

    def __init__(self, request):
        self._after_deferreds = []
        self.request = request

    def after(self):
        """
        Return a deferred that will fire after the request is finished.

        :returns: a new :class:`twisted.internet.defer.Deferred` for each call
            to this function.

        """

        d = Deferred()
        self._after_deferreds.append(d)
        return d

    def finish(self):
        for d in self._after_deferreds:
            d.callback(self)


class Manager(object):
    """
    The request manager coordinates state during each active request.

    """

    def __init__(self):
        self.requests = {}

    def after_response(self, request, fn, *args, **kwargs):
        """
        Call the given callable after the given request has its response.

        :argument request: the request to piggyback
        :argument fn: a callable that takes at least two arguments, the request
            and the response (in that order), along with any additional
            positional and keyword arguments passed to this function which will
            be passed along. If the callable returns something other than
            ``None``, it will be used as the new response.

        """

        self.requests[request]["callbacks"].append((fn, args, kwargs))

    def request_started(self, request):
        self.requests[request] = {"callbacks": [], "resources": {}}

    def request_served(self, request, response):
        request_data = self.requests.pop(request)
        for callback, args, kwargs in request_data["callbacks"]:
            callback_response = callback(response, *args, **kwargs)
            if callback_response is not None:
                response = callback_response
        return response


@attributes(
    [
        Attribute(name="headers", default_factory=Headers),
        Attribute(name="path"),
        Attribute(name="method", default_value="GET"),
        Attribute(
            name="messages", default_factory=list, exclude_from_cmp=True,
        ),
    ],
)
class Request(object):
    def flash(self, message):
        self.messages.append(_Message(content=message))


@attributes(
    [
        Attribute(name="content", exclude_from_init=True),
        Attribute(name="code", default_value=200),
        Attribute(name="headers", default_factory=MutableHeaders),
    ],
)
class Response(object):
    def __init__(self, content=""):
        self.content = content

    @property
    def status(self):
        return HTTP_STATUS_CODES[self.code]


@attributes(["content"])
class _Message(object):
    """
    A flashed message.

    """


def redirect(to, code=302):
    """
    Return a redirect response to the given URL.

    """

    return Response(headers=MutableHeaders([("Location", [to])]), code=code)
