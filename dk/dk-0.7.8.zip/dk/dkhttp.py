# -*- coding: utf-8 -*-

"""Various conveniences for dealing with the http protocol (requests,
   responses, etc.)
"""

# pylint:disable=C0323,W0621
# C0323 idiomatic print >>fp, usage
# W0621 request is a function defined in the module
#       and also used an argument name.

from dk import dklogger

logger = dklogger.dklogger(__name__, debug=0, info=0)

import urlparse, random, hashlib
import cStringIO as StringIO

from django.conf import settings
from django import http, template
from django.core import context_processors
from django.utils.cache import patch_vary_headers
from django.contrib.sessions.models import Session
import cPickle as pickle

if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange


class DkHttpError(Exception):
    "Base exception for dk http."
    pass


class ImmediateHttpResponse(DkHttpError):
    """This exception is used to interrupt the flow of processing to immediately
       return a custom HttpResponse.

       Common uses include::

           * for authentication (like digest/OAuth)
           * for throttling

       (from TastyPie).
    """
    _response = http.HttpResponse("Nothing provided.")

    def __init__(self, response):
        self._response = response

    @property
    def response(self):
        return self._response


class ImmediateHttpResponseMiddleware(object):
    """Middleware that handles ImmediateHttpResponse exceptions, allowing us
       to return a response from deep in form handling code.
    """
    def process_exception(self, _request, exception):
        if isinstance(exception, ImmediateHttpResponse):
            return exception.response
        return None

#
#   Naming the HTTP response codes.
#

class HttpAccepted(http.HttpResponse):
    status_code = 202


class HttpNoContent(http.HttpResponse):
    status_code = 204


class HttpMultipleChoices(http.HttpResponse):
    status_code = 300


class HttpSeeOther(http.HttpResponse):
    status_code = 303


class HttpNotModified(http.HttpResponse):
    status_code = 304


class HttpBadRequest(http.HttpResponse):
    status_code = 400


class HttpUnauthorized(http.HttpResponse):
    status_code = 401


class HttpForbidden(http.HttpResponse):
    status_code = 403


class HttpNotFound(http.HttpResponse):
    status_code = 404


class HttpMethodNotAllowed(http.HttpResponse):
    status_code = 405


class HttpConflict(http.HttpResponse):
    status_code = 409


class HttpGone(http.HttpResponse):
    status_code = 410


class HttpUnprocessableEntity(http.HttpResponse):
    status_code = 422


class HttpTooManyRequests(http.HttpResponse):
    status_code = 429


class HttpApplicationError(http.HttpResponse):
    status_code = 500


class HttpNotImplemented(http.HttpResponse):
    status_code = 501


def debug_info_string(request):
    "Return info about the request as a string."
    fp = StringIO.StringIO()
    print >>fp
    print >>fp, '===', request.method, repr(request.META.get('PATH_INFO',''))
    print >>fp, '-- Referrer: -------------------'
    print >>fp, '  ', request.META.get('HTTP_REFERER')
    if hasattr(request, 'TOKENS'):
        print >>fp, 'TOKENS: -------------------------'
        for k, v in request.TOKENS.items():
            print >>fp, '  ', k, '=', v
    print >>fp, 'Cookies:-------------------------'
    for k, v in request.COOKIES.items():
        print >>fp,'  ', k, '=', v
    print >>fp, 'Session:-------------------------'
    for k, v in request.session.items():
        print >>fp,'  ', k, '=', repr(v)

        if k.endswith('sessionid'):
            try:
                s = Session.objects.get(pk=v)
                for sk, sv in s.get_decoded().items():
                    print >>fp,'    ', sk, '=', repr(sv)[:75]
            except:
                pass

    if request.method == "POST":
        print >>fp, 'POST:----------------------------'
        try:
            for k, v in request.POST.items():
                print >>fp, '  ', repr(k), '=',
                if k.endswith('[]'):
                    print >>fp, request.POST.getlist(k)
                else:
                    print >>fp, repr(v)

        except IOError:
            pass
        
    print >>fp, '================================='
    print >>fp
    txt = fp.getvalue()
    return txt


def debug_info(request):
    "Display info about the contents of the request."
    if settings.DEBUG:  # or settings.TESTING:
        print debug_info_string(request)
        return
        #
        #
        # print
        # try:
        #     print '===', request.method, request.META.get('PATH_INFO')
        # except:
        #     print '===', request.method, repr(request.META.get('PATH_INFO'))
        # print '   request.user:', request.user
        # print '-- Referrer: --------------------'
        # print '  ', request.META.get('HTTP_REFERER')
        # if hasattr(request, 'TOKENS'):
        #     print 'TOKENS: -------------------------'
        #     for k, v in request.TOKENS.items():
        #         print '  ', k, '=', pprint.pformat(v, indent=6)
        # print 'Cookies:-------------------------'
        # for k, v in request.COOKIES.items():
        #     print '  ', k, '=', v
        # print 'Session:-------------------------', type(request.session)
        # for k, v in request.session.items():
        #     print '  ', k, '=', repr(v)[:100]
        # if request.method == "POST":
        #     print 'POST:----------------------------'
        #     for k, v in sorted(request.POST.items()):
        #         print '  ', k, '=',
        #         if k.endswith('[]'):
        #             print request.POST.getlist(k)
        #         else:
        #             print repr(v)
        #
        # print '================================='
        # print
        #
        #pprint.pprint(request)


def http_accept_language(browserval):
    """Parse the HTTP_ACCEPT_LANGUAGE header from the browser.
    """
    res = []
    for lang in browserval.lower().split(','):
        pref = lang.split(';')
        lval = pref[0]
        lval_prefix = lval.split('-')[0]
        
        if len(pref) == 2:
            pval = pref[1].split('=')[1]
            res.append((float(pval), lval, lval_prefix))
        else:
            res.append((1.0, lval, lval_prefix))
    res.sort(reverse=True)
    return res


def negotiate_language(accept_lang_header, supported_langs):
    """Inspired by the PHP function with similar name.  Takes as
       arguments the HTTP_ACCEPT_LANGUAGE string from the browser, and
       a list of languages the application supports (in decreasing
       order of preference, e.g. ['en-us', 'en', 'no-nn']).  The
       qualifier is recognized and languages without qualifier are
       rated highest. The qualifier will be decreased by 10% for
       partial matches (i.e. 'prefix-match').

       Cf. http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
    """
    alangs = http_accept_language(accept_lang_header)
    slangs = dict((slang.lower(), 0.0) for slang in supported_langs)
    bestlang = dict((slang.lower(), None) for slang in supported_langs)

    for q, lang, prefix in alangs:
        for slang in slangs:
            if lang == slang:
                if q > slangs[slang]:
                    slangs[slang] = q
                    bestlang[slang] = lang

    for q, lang, prefix in alangs:
        for slang in slangs:
            sprefix = slang.split('-')[0]
            if sprefix == prefix:
                if q * 0.9 > slangs[slang]:
                    slangs[slang] = q * 0.9
                    bestlang[slang] = lang

    qval = 0.0
    selected = supported_langs[0]
    for slang, q in slangs.items():
        if q > qval:
            q = qval
            selected = slang
    
    if 0 and settings.DEBUG:
        print "SUPPORTED:", supported_langs
        print "ALANGS:", alangs
        print "SLANGS:", slangs
        print "BESTLANG:", bestlang
        print "SELECTED:", bestlang.get(selected, supported_langs[0])
        
    return selected

#print negotiate_language('no-nb,en;q=0.5', ['*', 'en', 'en-us'])
# negotiate_language('en-us,en;q=0.5', ['no', 'en-uk']) == 'en-uk'


def no_cache(httpresponse):
    "Set required headers to prevent caching of response."
    # overwrite these headers..
    httpresponse['PRAGMA'] = 'NO-CACHE'
    httpresponse['Expires'] = '-1'
    httpresponse['Cache-Control'] = 'max-age=0, no-store, must-revalidate, proxy-revalidate'

    # merge vary on cookie header..
    patch_vary_headers(httpresponse, ['Cookie'])
    return httpresponse


def create_csrf_cookie(request=None):
    """Create a cross site request forgery cookie (use Django's version if we
       can.
    """
    if request is not None:
        csrftoken = unicode(context_processors.csrf(request)['csrf_token'])
        logger.debug("CREATING CSRF COOKIE: %s", csrftoken)
        return csrftoken
    else:
        csrftoken = hashlib.md5('%s%s' % (randrange(0, 2 ** 63),
                                     settings.SECRET_KEY)).hexdigest()
        logger.debug("CREATING CSRF (MD5) COOKIE: %s", csrftoken)
        return csrftoken


def render_to_response(tmpl, page, status_code=None, cache=True,
                       requestcontext=False, **headers):
    """A render_to_response clone that sets the CSRF cookie for forms that
       require this.

       Usage::

#            def myview(request, ...)
#                page = adt.page(request)
#                page.myform = MyForm(request, ...)
#                if page.myform.valid:
#                    #...
#                return dkhttp.response('mytemplate.html', page)

    """
    t = template.loader.get_template(tmpl)

    if settings.DEBUG:
        import inspect
        page.dbg_template_name = tmpl
        caller = inspect.currentframe().f_back
        page.dbg_view_name = '%s[%s]:%s' % (
            caller.f_code.co_filename,
            caller.f_lineno,
            caller.f_code.co_name)
        del caller  # don't keep frame objects around

    if requestcontext:
        ctx = template.context.RequestContext(page.request, page)
    else:
        ctx = template.context.Context(page)

    txt = t.render(ctx)

    response = http.HttpResponse(txt)
    request = page.request

    if any([getattr(val, '_needs_viewstate', False) for val in page.values()]):
        #print "NEEDS VIEWSTATE" + '\n' * 10
        if settings.DEBUG:
            # the user could have several windows open, so don't
            # delete viewstate unless we're in DEBUG mode (they
            # accumulate and clutter up the debugging environment).
            for key in request.session.keys():
                if key.startswith('viewstate.'):
                #if key.startswith('vstate2.'):
                    del request.session[key]
        else:
            pass
            #print "NO_NEED_VIEWSTATE" + '\n' * 10

        # VIEWSTATE -> session
        # vstate + viewstate protocol version number + unique page uuid
        sessionkey = 'vstate2.' + page.uuid
        request.session[sessionkey] = pickle.dumps(page.viewstate())

    cookieval = request.META.get(
        "CSRF_COOKIE",
        request.COOKIES.get(settings.DKCSRF_COOKIE_NAME))

    if request.method == 'GET':
        for frm in page.forms:
            if getattr(frm, 'csrfcookie', False):
                if cookieval:
                    frm.csrfcookie = cookieval
                else:
                    cookieval = frm.csrfcookie

        logger.debug('meta-csrf: %r csrf-cookie: %r  form-csrfs: %r',
                     request.META.get("CSRF_COOKIE", ""),
                     request.COOKIES.get(settings.DKCSRF_COOKIE_NAME),
                     [getattr(frm, 'csrfcookie', "") for frm in page.forms])

    response.set_cookie(settings.DKCSRF_COOKIE_NAME,
                        cookieval,
                        max_age=60 * 60 * 24 * 7 * 52,
                        domain=settings.CSRF_COOKIE_DOMAIN,
                        path=settings.CSRF_COOKIE_PATH,
                        secure=settings.CSRF_COOKIE_SECURE)

    patch_vary_headers(response, ('Cookie',))
    response.csrf_processing_done = True

    if not cache:
        response['PRAGMA'] = 'NO-CACHE'
        response['Expires'] = '-1'
        response['Cache-Control'] = 'max-age=0, no-store, must-revalidate'

    logger.debug("headers %r", headers)
    for hdr, val in headers.items():
        response[hdr] = val
    if status_code is not None:
        response.status_code = status_code

    if settings.TESTING:
        response.page = page
        response.template_name = tmpl

    return response


def response(*args, **kwargs):
    """Similarly to Django's distinction between render_to_response and
       response, this function forces the use of a RequestContext object.
       In particular, this means that any ``user`` and ``perms`` context
       variables will be overwritten.
    """
    return render_to_response(*args, requestcontext=True, **kwargs)


def referring_host(request):
    """Return referring host (or 'unknown').
    """
    # return self._request.get_host().split(':')[0]

    referer = request.META.get('HTTP_REFERER','')
    u = urlparse.urlparse(referer)
    host = 'unknown'
    try:
        netloc = u.netloc
        host, _ = netloc.split('.', 1)
    except:
        pass

    return host


def current_host(request):
    "Return the current host (if known)."
    return request.META.get('HTTP_HOST','')


def request(fn):
    "Decorator that wraps django request objects in Request objects."
    return fn


class Request(object):
    """Don't use..(?)
    """
    def __init__(self, request):
        self._request = request
        self._host = None

    def __getattr__(self, key):
        """Treat Request objects as real objects using .foo notation
           instead of ['foo'] notation.
        """
        return getattr(self._request, key)

    def items(self, *filtr):
        """Yield parameters to the request (both GET & POST).
           Optionally filter by parameters.
        """
        if filtr:
            for item in filtr:
                yield item, self._request.REQUEST.get(item)
        else:
            for key in self._request.REQUEST.keys():
                yield key, self._request.REQUEST[key]

    @property
    def host(self):
        """Return referring host (or 'unknown').
        """
        # return self._request.get_host().split(':')[0]
        
        if self._host is None:
            referer = self._request.META.get('HTTP_REFERER','')
            u = urlparse.urlparse(referer)
            host = 'unknown'
            try:
                netloc = u.netloc
                host, _ = netloc.split('.', 1)
            except:
                pass
            self._host = host
            
        return self._host

    def redirect_back(self, default=''):
        """Redirect whence we came, pass start, don't collect $100.
        """
        url = self._request.META.get('HTTP_REFERER', default)
        return http.HttpResponseRedirect(url)


def serious_error(request, message, **kw):
    """Return an error page containing message.
    """
    from dk import collections as adt
    page = adt.page(request)
    page.message = message
    page.args = [dict(key=k, value=v) for k, v in kw.items()]
    return render_to_response('serious-error.html', page)
