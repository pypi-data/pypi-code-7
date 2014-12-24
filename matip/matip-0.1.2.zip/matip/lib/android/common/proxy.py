#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import string
from command import Command
from matip.lib.android.server.config import Config
import logging as log
try:
    import http.client as httplib
    from urllib import request as url_request
    from urllib import parse
except ImportError: # above is available in py3+, below is py2.7
    import httplib as httplib
    import urllib2 as url_request
    import urlparse as parse
log.basicConfig(
    format = "%(levelname)s: %(message)s",
    level = log.DEBUG
    )

def execute(command, params):
    """
    Send a command to the remote server.

    Any path subtitutions required for the URL mapped to the command should be
    included in the command parameters.

    :Args:
     - command - A string specifying the command to execute.
     - params - A dictionary of named parameters to send with the command as
       its JSON payload.
    """
    host = Config.PROXY_HOST
    port = Config.SYSTEM_PORT
    data = json.dumps(params)
    path = string.Template(command[1]).substitute(params)
    url = "http://%s:%s/wd/hub%s" % (host,port,path)
    return _request(command[0], url, body=data)

def _request( method, url, body=None):
    """
    Send an HTTP request to the remote server.

    :Args:
     - method - A string for the HTTP method to send the request with.
     - url - A string for the URL to send the request to.
     - body - A string for request body. Ignored unless method is POST or PUT.

    :Returns:
      A dictionary with the server's parsed JSON response.
    """
    if body and method != "POST" and method != "PUT":
        body = None
    opts = {}
    opts["url"] = url
    opts["method"] = method
    opts["json"] = body
    log.debug("Making http request with opts: %s" % json.dumps(opts))
    request = Request(url, data=body,method=method)
    request.add_header('Accept', 'application/json')
    request.add_header('Content-Type', 'application/json;charset=UTF-8')

    opener = url_request.build_opener(url_request.HTTPRedirectHandler())
    resp = opener.open(request)
    statuscode = resp.code
    if not hasattr(resp, 'getheader'):
	if hasattr(resp.headers, 'getheader'):
	    resp.getheader = lambda x: resp.headers.getheader(x)
	elif hasattr(resp.headers, 'get'):
	    resp.getheader = lambda x: resp.headers.get(x)
    data = resp.read()
    try:
        if 399 < statuscode < 500:
            return {'status': statuscode, 'value': data}
        if 300 <= statuscode < 304:
            return request('GET', resp.getheader('location'))
        body = data.decode('utf-8').replace('\x00', '').strip()
        content_type = []
        if resp.getheader('Content-Type') is not None:
            content_type = resp.getheader('Content-Type').split(';')
        if not any([x.startswith('image/png') for x in content_type]):
            try:
                data = json.loads(body.strip())
            except ValueError:
                if 199 < statuscode < 300:
                    status = 0
                else:
                    status = 13
                return {'status': status, 'value': body.strip()}

            assert type(data) is dict, (
                'Invalid server response body: %s' % body)
            assert 'status' in data, (
                'Invalid server response; no status: %s' % body)
            if 'value' not in data:
                data['value'] = None
            log.debug("Proxied response received: %s" % json.dumps(data))
            return data
        else:
            data = {'status': 0, 'value': body.strip()}
            log.debug("Proxied response received: %s" % json.dumps(data))
            return data
    finally:
        resp.close()


class Request(url_request.Request):
    """
    Extends the url_request.Request to support all HTTP request types.
    """

    def __init__(self, url, data=None, method=None):
        """
        Initialise a new HTTP request.

        :Args:
        - url - String for the URL to send the request to.
        - data - Data to send with the request.
        """
        if method is None:
            method = data is not None and 'POST' or 'GET'
        elif method != 'POST' and method != 'PUT':
            data = None
        self._method = method
        url_request.Request.__init__(self, url, data=data)

    def get_method(self):
        """
        Returns the HTTP method used by this request.
        """
        return self._method
