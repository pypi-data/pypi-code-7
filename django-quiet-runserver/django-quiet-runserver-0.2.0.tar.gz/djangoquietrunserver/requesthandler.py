import socket
import sys
from django.conf import settings
from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler
from django.utils.six.moves import socketserver


class QuieterWSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        # Don't bother logging requests for admin images or the favicon.
        admin_static = settings.STATIC_URL + "admin/"
        if (self.path.startswith(admin_static)
                or self.path == '/favicon.ico'):
            return

        try:
            method, path, http_version = args[0].split(' ')
            code = args[1]
            size = args[2]

            method_map = {'GET': 'G', 'POST': 'P'}
            method = method_map.get(method, method)
            if '?' in path:
                path, querystring = path.split('?', 2)
                path = '{0}\n  ?{1}'.format(path, querystring)
            msg = '{code} {method} {path}\n'.format(
                code=code, method=method, path=path)
        except:
            msg = (format % args) + "\n"

        # Utilize terminal colors, if available
        if args[1][0] == '2':
            # Put 2XX first, since it should be the common case
            msg = self.style.HTTP_SUCCESS(msg)
        elif args[1][0] == '1':
            msg = self.style.HTTP_INFO(msg)
        elif args[1] == '304':
            return  # Ignore 304 requests
        elif args[1][0] == '3':
            msg = self.style.HTTP_REDIRECT(msg)
        elif args[1] == '404':
            msg = self.style.HTTP_NOT_FOUND(msg)
        elif args[1][0] == '4':
            msg = self.style.HTTP_BAD_REQUEST(msg)
        else:
            # Any 5XX, or any other response
            msg = self.style.HTTP_SERVER_ERROR(msg)

        sys.stderr.write(msg)


def run(addr, port, wsgi_handler, ipv6=False, threading=False):
    server_address = (addr, port)
    if threading:
        httpd_cls = type(str('WSGIServer'), (socketserver.ThreadingMixIn, WSGIServer), {})
    else:
        httpd_cls = WSGIServer
    httpd = httpd_cls(server_address, QuieterWSGIRequestHandler, ipv6=ipv6)
    httpd.set_app(wsgi_handler)
    httpd.serve_forever()
