#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket
import tempfile
try:
    import http.client as httplib
    from urllib import request as url_request
except ImportError: # above is available in py3+, below is py2.7
    import httplib as httplib
    import urllib as url_request


def configureApp(app):
    if app[:4].lower() == "http":
        tmp_dir = tempfile.mkdtemp()
        rand_num = str(time.time()).replace(".","")
        tmp_path = os.path.join(tmp_dir,rand_num + ".apk")
        configureDownloadedApp(app,tmp_path)
        return tmp_path
    else:
        configureLocalApp(app)
        return app


def configureLocalApp(app):
    ext = app[-4:].lower()
    if ext == ".apk":
        if not os.path.exists(app):
            msg = "App is not exists: %s" % app
            raise Exception(msg)
    else:
        msg = "Using local app,but didn't end in .apk"
        raise Exception(msg)


def configureDownloadedApp(app,path):
    ext = app[-4:].lower()
    if ext == ".apk":
        downloadApp(app,path)
        if os.path.getsize(path) < 1024:
            msg = "Failed downliading app from appUrl(%s)" % app
            raise Exception(msg)
    else:
        msg = "App URL(%s) didn't seem to point to a .apk file" % app
        raise Exception()


def downloadApp(self,app,new_app):
    try:
        #set urllib timeout
        socket.setdefaulttimeout(300)  
        url_request.urlretrieve(app,new_app)
    except:
        msg = "Failed downliading app from appUrl(%s)" % app
        raise Exception(msg)




    
