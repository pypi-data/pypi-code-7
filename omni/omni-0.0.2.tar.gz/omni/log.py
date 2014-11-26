#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.

"""
Logging utilities.
"""

class WSGIRequestLogMiddleware(object):
    """
    Simple WSGI middleware to perform request logging.

    Logs each WSGI
    """
    def __init__(self, application):
        self._application = application

    def start_response(self, status, header, exc_info=None):
        pass

    def __call__(self, environ, start_response):
        return self._application(environ, start_response)
