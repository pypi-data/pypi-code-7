from __future__ import absolute_import

import urllib

from tornado import httpclient
from tornado import gen

from consul import base


__all__ = ['Consul']


class HTTPClient(object):
    def __init__(self, host='127.0.0.1', port=8500):
        self.host = host
        self.port = port
        self.base_uri = 'http://%s:%s' % (self.host, self.port)
        self.client = httpclient.AsyncHTTPClient()

    def uri(self, path, params=None):
        uri = self.base_uri + path
        if not params:
            return uri
        return '%s?%s' % (uri, urllib.urlencode(params))

    def response(self, response):
        return base.Response(response.code, response.headers, response.body)

    @gen.coroutine
    def _request(self, callback, request):
        try:
            response = yield self.client.fetch(request)
        except httpclient.HTTPError, e:
            if e.code == 599:
                raise base.Timeout
            response = e.response
        raise gen.Return(callback(self.response(response)))

    def get(self, callback, path, params=None):
        uri = self.uri(path, params)
        return self._request(callback, uri)

    def put(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)
        request = httpclient.HTTPRequest(uri, method='PUT', body=data)
        return self._request(callback, request)

    def delete(self, callback, path, params=None):
        uri = self.uri(path, params)
        request = httpclient.HTTPRequest(uri, method='DELETE')
        return self._request(callback, request)


class Consul(base.Consul):
    def connect(self, host, port):
        return HTTPClient(host, port)
