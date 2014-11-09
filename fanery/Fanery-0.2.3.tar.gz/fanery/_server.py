"""
Third party WSGI Server setup helper function.

Mostly usefull during development and testing.
"""
__all__ = ['start_wsgi_server']

from _wsgi import build_handler
import _config as conf

import logging
logger = logging.getLogger('fanery.server')


def start_wsgi_server(wsgi_app=None, host='127.0.0.1', port=9000,
                      bjoern=True, gevent=False, cherrypy=False,
                      remote_debugger=False, ssl=False, **argd):

    if remote_debugger is True:
        from _crypto import nacl_random, nacl_sha256
        import rpdb2
        rpdb2_passwd = nacl_sha256(nacl_random(16))
        rpdb2.start_embedded_debugger(rpdb2_passwd,
                                      fAllowRemote=True,
                                      fAllowUnencrypted=False)
        logger.debug("rpdb2 remote debugger started with password '%s'" % rpdb2_passwd)   # noqa
        del rpdb2_passwd

    if wsgi_app is None:
        wsgi_app = build_handler(**argd)

    if argd.pop('gzip', conf.IS_DEVELOPMENT) is True:
        from paste.gzipper import make_gzip_middleware
        wsgi_app = make_gzip_middleware(wsgi_app, None)

    logger.info("serving on %s://%s:%s" % ('https' if ssl else 'http', host, port))     # noqa

    if ssl is True:
        from werkzeug.serving import run_simple

        params = dict(ssl_context=argd.get('ssl_context', 'adhoc'),
                      use_reloader=argd.get('use_reloader', True),
                      use_debugger=argd.get('use_debugger', True),
                      use_evalex=argd.get('use_evalex', True),
                      threaded=argd.get('threaded', True))

        try:
            run_simple(host, port, wsgi_app, **params)
        except KeyboardInterrupt:
            pass

    elif cherrypy is True:
        import cherrypy

        cherrypy.tree.graft(wsgi_app, '/')

        cherrypy.config.update({
            'engine.autoreload.on': True,
            'log.screen': True,
            'server.socket_port': port,
            'server.socket_host': host
        })

        try:
            cherrypy.engine.start()
            cherrypy.engine.block()
        except KeyboardInterrupt:
            cherrypy.engine.stop()

    elif gevent is True:
        from gevent.wsgi import WSGIServer

        try:
            WSGIServer((host, port), wsgi_app).serve_forever()
        except KeyboardInterrupt:
            pass

    elif bjoern is True:
        import bjoern

        try:
            bjoern.run(wsgi_app, host, port)
        except KeyboardInterrupt:
            pass

    else:
        from wsgiref.simple_server import make_server

        try:
            make_server(host, port, wsgi_app).serve_forever()
        except KeyboardInterrupt:
            pass
