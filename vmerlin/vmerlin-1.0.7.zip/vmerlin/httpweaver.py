#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

from .genericweaver import BaseWeaver
from .helpers import Helpers

# ----------------------------------------------------------------------------

class BaseHttpWeaver(BaseWeaver):
    def __init__(self, flavor, logFactory, args, dispatcher):
        super(BaseHttpWeaver,self).__init__(flavor, logFactory, args, dispatcher)
    
    def dispatch(self, startTime, endTime, props, error=None):
        if self.logger.traceEnabled:
            self.logger.trace("'%s' in %d nanos" % (props['label'], BaseWeaver.nanosDiff(startTime, endTime)))
        return super(BaseHttpWeaver, self).dispatch(startTime, endTime, props, error)

    @staticmethod
    def breakDownUri(uri, props):
        props['uri'] = uri
        
        path = uri
        queryPos = uri.find('?')
        if queryPos >= 0:
            props['query'] = uri[queryPos+1:]
            path = uri[0:queryPos]
        
        props['path'] = path
        # nothing to do if root or ends in '/'
        if (path == '/') or path.endswith('/'):
            return props

        suffixPos = path.rfind('.')
        filenamePos = path.rfind('/')
        if (suffixPos > 0) and (filenamePos >= 0) and (filenamePos < (suffixPos - 1)):
            props['filename'] = path[filenamePos+1:suffixPos]
            props['filetype'] = path[suffixPos + 1:].lower()
            props['path'] = path[0:filenamePos]

        return props
    
    @staticmethod
    def convertSizeValue(value):
        if isinstance(value, ( str, unicode )):
            if len(value) <= 0:
                return -1
            else:
                return int(Helpers.toSafeString(value))
        elif isinstance(value, ( int, long )):
            return value
        else:
            return -1

    @staticmethod
    def parseProtocol(protocolLine, props=None):
        if Helpers.isEmpty(protocolLine):
            return props

        pos = protocolLine.find('/')
        if pos <= 0:
            return props

        if props is None:
            props = {}


        props['protocol'] = protocolLine[0:pos]
        props['version'] = protocolLine[pos+1:]
        return props
    
    @staticmethod
    def fillRequestDetails(props=None, remoteAddress=None, remoteUser=None, method="UNKNOWN", uri='', userAgent=None, requestSize=-1):
        if props is None:
            props = {}

        props['flavor'] = 'http'
        BaseHttpWeaver.breakDownUri(Helpers.toSafeString(uri), props)
        props['protocol'] = 'HTTP'
        props['version'] = 'unknown'
        props['method'] = Helpers.toSafeString(method).upper()
        props['label'] = "%s %s" % (props['method'], props['uri'])
        
        requestSize = BaseHttpWeaver.convertSizeValue(requestSize)
        if requestSize > 0:
            props['requestsize'] = requestSize

        remoteAddress = Helpers.toSafeString(remoteAddress)
        remoteAddress = BaseWeaver.sanitizeRemoteAddress(remoteAddress)
        BaseWeaver.putIfValidString(props, 'remoteaddr', remoteAddress)
        BaseWeaver.putIfValidString(props, 'location', props.get('remoteaddr', None))

        BaseWeaver.putIfValidString(props, 'remoteuser', Helpers.toSafeString(remoteUser))
        BaseWeaver.putIfValidString(props, 'useragent', Helpers.toSafeString(userAgent))
        return props

    @staticmethod
    def fillResponseDetails(props=None, statusCode=-1, responseSize=-1):
        if props is None:
            props = {}
        
        props['statuscode'] = statusCode

        responseSize = BaseHttpWeaver.convertSizeValue(responseSize)
        if responseSize > 0:
            props['responsesize'] = responseSize

        return props
        
