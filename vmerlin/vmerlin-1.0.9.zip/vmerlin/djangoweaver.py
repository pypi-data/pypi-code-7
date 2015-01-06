#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys

from .helpers import Helpers
from .genericweaver import BaseWeaver
from .httpweaver import BaseHttpWeaver

class DjangoHttpWeaver(BaseHttpWeaver):
    DJANGO_TRACEID_HEADER = "HTTP_%s" % (BaseHttpWeaver.TRACEID_HEADER.upper().replace('-', '_'))

    @staticmethod
    def getRemoteAddress(request):
        """
        Returns the IP of the request, accounting for the possibility of being behind a proxy.
        See https://djangosnippets.org/snippets/2575/
        """
        ip = request.META.get("HTTP_X_FORWARDED_FOR", None)
        if ip:
            # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
            proxies = ip.split(", ") 
            ip = proxies[0]
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip

    def __init__(self, logFactory, args, dispatcher):
        super(BaseHttpWeaver,self).__init__("django-http", logFactory, args, dispatcher)

        from django.core.handlers.base import BaseHandler
        
        old_get_response = BaseHandler.get_response
        thisWeaver = self

        def get_response(self, request):
            '''
            Returns an HttpResponse object for the given django.http.request (HttpRequest)
            '''
            error = None
            startCorrelation = thisWeaver.startCorrelationContext('django', request.META.get(DjangoHttpWeaver.DJANGO_TRACEID_HEADER, None))
            startTime = BaseWeaver.timestampValue()
            try:
                response = old_get_response(self, request)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()
            endCorrelation = thisWeaver.endCorrelationContext(startCorrelation)

            props = { 
                'objecttype': 'django.core.handlers.base.BaseHandler',
                'function': 'get_response',
                'signature': '(self, request)'
            }

            BaseWeaver.setTraceEssenceCorrelation(props, startCorrelation, endCorrelation)

            # see https://docs.djangoproject.com/en/dev/ref/request-response/
            props = BaseHttpWeaver.fillRequestDetails(props=props,
                                              uri=request.get_full_path(),
                                              method=request.META.get('REQUEST_METHOD', 'UNKNOWN'),
                                              remoteAddress=DjangoHttpWeaver.getRemoteAddress(request),
                                              remoteUser=request.META.get('REMOTE_USER', ""),
                                              userAgent=request.META.get('HTTP_USER_AGENT', ""),
                                              requestSize=request.META.get('CONTENT_LENGTH', None))
            props['protocol'] = request.scheme.upper()

            if error is None:
                BaseHttpWeaver.fillResponseDetails(props=props, statusCode=response.status_code, responseSize=response.get('Content-Length', None))

            thisWeaver.dispatch(startTime, endTime, props, error)

            if error is None:
                return response
            else:
                raise error
        
        BaseHandler.get_response = get_response
        
