#!/usr/bin/python
# coding: utf-8

# The MIT License (MIT)
#
# Copyright (c) 2014 Carlos de Alfonso (caralla@upv.es)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import web
import sys
import threading
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
import sys, logging

class MyLogMiddleware:
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        return self.app(environ, start_response)

# This line enables to silent the calls from web.py
web.httpserver.LogMiddleware=MyLogMiddleware

def get_dispatcher():
    global dispatcher
    try:
        dispatcher
    except:
        dispatcher = SimpleXMLRPCDispatcher(allow_none = False, encoding = "UTF-8")
    return dispatcher

class rpc_server:
    def GET(self, url):
        return "please use root url for web browsing"
    def POST(self):
        dispatcher = get_dispatcher()
        response = dispatcher._marshaled_dispatch(web.webapi.data())
        web.header('Content-length', str(len(response)))
        return response

class web_server(rpc_server):
    pass

def start_server(web_class = 'web_server', port = 8080):
    urls = ('/RPC2', 'rpc_server', '(/.*)', web_class)
    sys.argv = [ sys.argv[0], str(port) ] + sys.argv[1:]
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()

def start_server_in_thread(web_class = 'web_server', port = 80):
    thread = threading.Thread(args = (web_class, port), target=start_server)
    thread.daemon = True
    thread.start()
    return thread
