try:
    import xmlrpclib
    from xmlrpclib import *
except ImportError:
    # Python 3.0 portability fix...
    import xmlrpc.client as xmlrpclib
    from xmlrpc.client import *

import httplib
import socket


class ServerProxy(xmlrpclib.ServerProxy):

    def __init__(self, uri, transport=None, encoding=None, verbose=0,
                 allow_none=0, use_datetime=0, timeout=None):
        if timeout is not None:
            transport = TimeoutTransport(use_datetime, timeout)
        xmlrpclib.ServerProxy.__init__(self, uri, transport, encoding, verbose,
                                       allow_none, use_datetime)


class TimeoutTransport(xmlrpclib.Transport):

    def __init__(self, use_datetime=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        xmlrpclib.Transport.__init__(self, use_datetime)
        self.timeout = timeout

    def make_connection(self, host):
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        chost, self._extra_headers, x509 = self.get_host_info(host)
        self._connection = host, httplib.HTTPConnection(
            chost, timeout=self.timeout
        )
        return self._connection[1]