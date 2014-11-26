#
# This is a sample startup file
# It shows how to declare a Beaker sessions middleware
#

import zope.app.wsgi
from beaker.middleware import SessionMiddleware
from zope.component import queryUtility
from ztfy.beaker.metadirectives import IBeakerSessionConfiguration

import os
os.environ['NLS_LANG'] = 'FRENCH_FRANCE.UTF8'

try:
    import psyco
    psyco.profile()
except:
    pass


def application_factory(global_conf):
    zope_conf = global_conf['zope_conf']
    app = zope.app.wsgi.getWSGIApplication(zope_conf)

    beaker_session = queryUtility(IBeakerSessionConfiguration, name=u'')
    if beaker_session is not None:
        options = beaker_session.getConfigurationDict()
        beaker_app = SessionMiddleware(app, options)
    else:
        beaker_app = app

    def wrapper(environ, start_response):
        vhost = ''
        vhost_skin = environ.get('HTTP_X_VHM_SKIN')
        if vhost_skin and \
           (not environ.get('CONTENT_TYPE', '').startswith('application/json')) and \
           (not environ.get('PATH_INFO', '').startswith('/++skin++')):
            vhost = '/++skin++' + vhost_skin
        url_scheme = environ.get('wsgi.url_scheme', 'http')
        vhost_root = environ.get('HTTP_X_VHM_ROOT', '')
        if (url_scheme == 'https') or (vhost_root and (vhost_root != '/')):
            vhost += '%s/++vh++%s:%s:%s/++' % (vhost_root,
                                               url_scheme,
                                               environ.get('SERVER_NAME', ''),
                                               environ.get('SERVER_PORT', '80'))
        environ['PATH_INFO'] = vhost + environ['PATH_INFO']
        return beaker_app(environ, start_response)

    return wrapper
