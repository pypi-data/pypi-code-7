"""
Fanery wsgi handler.
"""
__all__ = ['build_handler']

from mimetypes import guess_type, add_type
add_type('application/json', '.json')

from webob import Response
from webob.dec import wsgify
from webob.static import FileApp, DirectoryApp
from webob.exc import HTTPBadRequest, HTTPNotFound, HTTPNotImplemented

from _term import (
    Hict, normalize_filename, parse_json, to_simple, to_json,
    is_file_path, is_dir_path, is_sequence, is_generator
)
from _service import consume, lookup, traceback
from _autoreload import trigger_autoreload
from _state import State
from _exc import NotFound
from _version import __version__
import _config as conf

SERVER = 'Fanery/%s' % __version__
CONTENT_TYPE = 'text/plain'
CHARSET = 'utf8'
ENCODING_ERROR = 'Wrong request encoding, must be %s.' % CHARSET
STRICT_HTML_HEADERS = {
    'X-Frame-Options': 'SAMEORIGIN',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': "default-src 'self' 'unsafe-eval'",
}

from os.path import normpath, basename, join
from tempfile import NamedTemporaryFile
from os import link, unlink, chmod
from stat import S_IRUSR
from cgi import FieldStorage

import logging
logger = logging.getLogger('fanery.wsgi')


class BrokenUpload:
    pass


def _cgi_FieldStorage__make_file__patch(self, binary=None):
    '''monkey patch for FieldStorage.make_file

    Use named temporary file which allow then to create
    a permanent link after successfull upload and so
    avoid copy overhead.'''
    return NamedTemporaryFile(dir=conf.UPLOAD_DIRPATH)

FieldStorage.make_file = _cgi_FieldStorage__make_file__patch


def _permanent(temp_file):
    '''Create read-only hard link and close the given temporary file.'''
    dest_path = join(conf.UPLOAD_DIRPATH, basename(temp_file.filename))
    link(temp_file.file.name, dest_path)
    chmod(dest_path, S_IRUSR)
    return dest_path


def _param_value(term, links):
    if not isinstance(term, FieldStorage):
        return term
    elif term.done == -1:
        return BrokenUpload
    else:
        link = _permanent(term)
        links.add(link)
        return link


@wsgify
def handler(req):

    # requests are expected to be submitted in UTF-8

    try:
        req.charset = CHARSET
    except:
        return HTTPBadRequest(ENCODING_ERROR, server=SERVER)

    # parse request and consume service

    headers = {'Content-Security-Policy': "default-src 'none'"}
    is_development = conf.IS_DEVELOPMENT
    uploads = set()

    try:
        argd, params, path, = Hict(), req.params, req.path

        # parse request parameters
        for key in set(params.keys()):
            if not key.startswith('_'):
                if key.endswith('[]'):
                    values = (_param_value(term, uploads)
                              for term in params.getall(key))
                    argd[key[:-2]] = tuple(value for value in values
                                           if value is not BrokenUpload)
                else:
                    value = _param_value(params[key], uploads)
                    if value is not BrokenUpload:
                        argd[key] = value

        if '_json_' in params:
            argd.update(parse_json(params['_json_']))

        # build request state
        _state_ = State(domain=req.host.split(':', 1)[0],
                        origin=req.client_addr or '127.0.0.1',
                        sid=None, profile=None, role=None,
                        ssl=bool(req.headers.get('X-Forwarded-Proto', req.scheme) == 'https'))                  # noqa

        # trigger service reload
        if is_development:
            trigger_autoreload()

        # service lookup
        fun, argv, ext, out = lookup(normpath(path))

        # RFD and XSS attack mitigation against JSON/JSONP Web APIs
        if fun.safe and not is_development:
            assert req.headers.get('X-Fanery-Call', None) == 'true', 'api-call'
            headers['Content-Disposition'] = 'attachment; filename=f.txt'

        # perform service call
        _, _, ret = consume(_state_, (path, fun, argv, ext, out), **argd)

        # keep uploaded files
        uploads.clear()
    except NotFound:
        return HTTPNotFound(server=SERVER)
    except NotImplementedError:
        return HTTPNotImplemented(server=SERVER)
    except UnicodeDecodeError:
        return HTTPBadRequest(ENCODING_ERROR, server=SERVER)
    except Exception, e:
        if is_development: traceback.print_exc()   # noqa
        res = HTTPBadRequest(content_type='text/plain', server=SERVER)
        error = dict(exc=e.__class__.__name__, err=e.args)
        res.body = to_json(to_simple(error))
        return res
    finally:
        # cleanup uploaded files on error
        for link in uploads:
            unlink(link)

    # build answer

    if fun.ssl is True:
        headers['Strict-Transport-Security'] = "max-age=31536000; includeSubDomains"                        # noqa

    if fun.static is True:

        if isinstance(ret, file):
            if ret.closed is False and fun.auto_close_file is True:
                ret.close()
            ret = ret.name

        headers['X-Content-Type-Options'] = 'nosniff'

        if fun.cache is not True:
            headers['Cache-Control'] = 'max-age=0, must-revalidate, no-cache, no-store'                     # noqa
            headers['Pragma'] = 'no-cache'
            headers['Expires'] = '0'

        if fun.accel is not None:
            headers['X-Accel-Redirect' if fun.accel == 'nginx' else 'X-Sendfile'] = ret                     # noqa
            return Response(server=SERVER, headerlist=headers.items())

        elif is_file_path(ret):

            if fun.force_download is True:
                headers['Content-Type'] = 'application/octet-stream'

                # Content-Disposition security considerations
                # http://tools.ietf.org/html/rfc6266#section-7
                if fun.content_disposition is True:
                    filename = normalize_filename(ret)
                    headers['Content-Disposition'] = 'attachment; filename="%s"' % filename                 # noqa
            else:
                headers['Content-Type'] = content_type = guess_type(ret)[0] or CONTENT_TYPE                 # noqa

                if content_type.startswith('text/'):
                    headers.update(STRICT_HTML_HEADERS)

            return FileApp(ret, server=SERVER, headerlist=headers.items())

        elif is_dir_path(ret):
            return DirectoryApp(ret, server=SERVER)

        else:
            return HTTPNotFound(server=SERVER)

    else:
        headers['Content-Type'] = content_type = guess_type(path)[0] or CONTENT_TYPE                        # noqa

        if content_type == 'text/html':
            headers.update(STRICT_HTML_HEADERS)

        res = Response(server=SERVER, charset=CHARSET,
                       headerlist=headers.items(),
                       content_type=content_type)

        if isinstance(ret, str):
            res.body = ret
        elif isinstance(ret, unicode):
            res.unicode_body = ret
        elif is_sequence(ret) or is_generator(ret):
            res.app_iter = ret
        elif isinstance(ret, file):
            res.body_file = ret
        else:
            res.body = repr(ret)

        cache = fun.cache
        if not cache:
            res.cache_expires(0)
        elif isinstance(cache, int):
            res.cache_expires(cache)
        else:
            res.cache_expires(86400)

        return res


def build_handler(wsgi_app=handler, profile=False, **argd):

    if profile is True:
        from linesman import middleware
        open(middleware.ENABLED_FLAG_FILE, 'w').close()
        wsgi_app = middleware.make_linesman_middleware(wsgi_app, **argd)
        logger.info("wsgi profiler path is %s" % wsgi_app.profiler_path)

    return wsgi_app
