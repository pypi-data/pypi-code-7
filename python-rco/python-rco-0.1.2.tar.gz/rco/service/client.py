# -*- coding: utf-8 -*-

import cherrypy
import rco.client
import base


def lookup (code, version):
    request = cherrypy.serving.request
    if not request.app:
        raise LookupError ('Cannot execute simple lookup outside the request process', -4001)
    result = request.app.service.naming.lookup (code, version)
    return result [0:2]


def Service (uri, service_key, gpg_homedir = None, gpg_key = None, gpg_password = None, ticket = None):
    return rco.client.Service (
        uri,
        service_key,
        gpg_homedir or base.config ('security.homedir', strict = True),
        gpg_key or base.config ('security.key', strict = True),
        gpg_password or base.config ('security.password', strict = True),
        ticket
    )

def get_service (service_code, version = None, ticket = None):
    url, key = lookup (service_code, version)
    return Service (url, key)

