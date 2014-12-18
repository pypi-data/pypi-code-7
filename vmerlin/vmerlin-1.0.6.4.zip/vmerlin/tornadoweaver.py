#!/usr/bin/env python
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys

from .genericweaver import BaseWeaver
from .httpweaver import BaseHttpWeaver

class TornadoHttpWeaver(BaseHttpWeaver):
    @staticmethod
    def getRemoteAddress(request):
        """
        Returns the IP of the request, accounting for the possibility of being behind a proxy.
        See http://stackoverflow.com/questions/9420886/retrieve-browser-headers-in-python
        """
        ip = request.headers.get('X-Forwarded-For', None)
        if ip:
            # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
            proxies = ip.split(", ") 
            ip = proxies[0]
        else:
            ip = request.remote_ip
        return ip
    
    def __init__(self, logFactory, args, dispatcher):
        super(TornadoHttpWeaver,self).__init__("tornado-http", logFactory, args, dispatcher)

        from tornado.web import RequestHandler
        old_execute = RequestHandler._execute
        thisWeaver = self

        # @gen.coroutine
        def _execute(self, transforms, *args, **kwargs):
            error = None
            startCorrelation = BaseWeaver.startCorrelationContext('tornado')
            startTime = BaseWeaver.timestampValue()
            try:
                response = old_execute(self, transforms, *args, **kwargs)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()
            endCorrelation = BaseWeaver.endCorrelationContext(startCorrelation)

            props = { 
                'objecttype': 'tornado.web.RequestHandler',
                'function': '_execute',
                'signature': '(self, transforms, args, kwargs)'
            }

            correlation = startCorrelation
            if (correlation is None) or (len(correlation) <= 0):
                correlation = endCorrelation
            if (not correlation is None) and (len(correlation) > 0):
                props['correlation'] = correlation

            request = self.request
            headers = request.headers
            props = BaseHttpWeaver.parseProtocol(request.version, props)
            props = BaseHttpWeaver.fillRequestDetails(props=props,
                                              uri=request.uri,
                                              method=request.method,
                                              requestSize=headers.get('Content-Length', None),
                                              remoteAddress=TornadoHttpWeaver.getRemoteAddress(request),
                                              # remoteUser=request.META.get('REMOTE_USER', ""),
                                              userAgent=headers.get('User-Agent', ""))

            if error is None:
                BaseHttpWeaver.fillResponseDetails(props=props,
                                                   statusCode=self.get_status(),
                                                   responseSize=self._headers.get('Content-Length', None))

            thisWeaver.dispatch(startTime, endTime, props, error)

            if error is None:
                return response
            else:
                raise error

        RequestHandler._execute = _execute