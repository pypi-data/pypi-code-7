import calendar
import datetime
import platform
import time
import socket
import urllib
import urlparse
import warnings

import pingpp
from pingpp import error, http_client, version, util, certificate_blacklist

try:
    import ssl
except ImportError:
    if util.is_appengine_dev():
        warnings.warn(
            'We were unable to import the ssl module due to a bug in the '
            'Google App Engine development server. For more details and '
            'suggested resolutions see: '
            'https://code.google.com/p/googleappengine/issues/detail?id=9246.'
            'Please alert us immediately at support@pingplusplus.com if this '
            'message appears in your production logs.')
    raise


def _encode_datetime(dttime):
    if dttime.tzinfo and dttime.tzinfo.utcoffset(dttime) is not None:
        utc_timestamp = calendar.timegm(dttime.utctimetuple())
    else:
        utc_timestamp = time.mktime(dttime.timetuple())

    return int(utc_timestamp)


def _api_encode(data):
    for key, value in data.iteritems():
        key = util.utf8(key)
        if value is None:
            continue
        elif hasattr(value, 'pingpp_id'):
            yield (key, value.pingpp_id)
        elif isinstance(value, list) or isinstance(value, tuple):
            for subvalue in value:
                yield ("%s[]" % (key,), util.utf8(subvalue))
        elif isinstance(value, dict):
            subdict = dict(('%s[%s]' % (key, subkey), subvalue) for
                           subkey, subvalue in value.iteritems())
            for subkey, subvalue in _api_encode(subdict):
                yield (subkey, subvalue)
        elif isinstance(value, datetime.datetime):
            yield (key, _encode_datetime(value))
        else:
            yield (key, util.utf8(value))


def _build_api_url(url, query):
    scheme, netloc, path, base_query, fragment = urlparse.urlsplit(url)

    if base_query:
        query = '%s&%s' % (base_query, query)

    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


class APIRequestor(object):

    _CERTIFICATE_VERIFIED = False

    def __init__(self, key=None, client=None):
        self.api_key = key

        from pingpp import verify_ssl_certs

        self._client = client or http_client.new_default_http_client(
            verify_ssl_certs=verify_ssl_certs)

    @classmethod
    def api_url(cls, url=''):
        warnings.warn(
            'The `api_url` class method of APIRequestor is '
            'deprecated and will be removed in version 2.0.'
            'If you need public access to this function, please email us '
            'at support@pingplusplus.com.',
            DeprecationWarning)
        return '%s%s' % (pingpp.api_base, url)

    @classmethod
    def _deprecated_encode(cls, stk, key, value):
        warnings.warn(
            'The encode_* class methods of APIRequestor are deprecated and '
            'will be removed in version 2.0. '
            'If you need public access to this function, please email us '
            'at support@pingplusplus.com.',
            DeprecationWarning, stacklevel=2)
        stk.extend(_api_encode({key: value}))

    @classmethod
    def encode_dict(cls, stk, key, value):
        cls._deprecated_encode(stk, key, value)

    @classmethod
    def encode_list(cls, stk, key, value):
        cls._deprecated_encode(stk, key, value)

    @classmethod
    def encode_datetime(cls, stk, key, value):
        cls._deprecated_encode(stk, key, value)

    @classmethod
    def encode_none(cls, stk, key, value):
        cls._deprecated_encode(stk, key, value)

    @classmethod
    def encode(cls, d):
        """
        Internal: encode a string for url representation
        """
        warnings.warn(
            'The `encode` class method of APIRequestor is deprecated and '
            'will be removed in version 2.0.'
            'If you need public access to this function, please email us '
            'at support@pingplusplus.com.',
            DeprecationWarning)
        return urllib.urlencode(list(_api_encode(d)))

    @classmethod
    def build_url(cls, url, params):
        warnings.warn(
            'The `build_url` class method of APIRequestor is deprecated and '
            'will be removed in version 2.0.'
            'If you need public access to this function, please email us '
            'at support@pingplusplus.com.',
            DeprecationWarning)
        return _build_api_url(url, cls.encode(params))

    def request(self, method, url, params=None):
        self._check_ssl_cert()
        rbody, rcode, my_api_key = self.request_raw(
            method.lower(), url, params)
        resp = self.interpret_response(rbody, rcode)
        return resp, my_api_key

    def handle_api_error(self, rbody, rcode, resp):
        try:
            err = resp['error']
        except (KeyError, TypeError):
            raise error.APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (rbody, rcode),
                rbody, rcode, resp)

        if rcode in [400, 404]:
            raise error.InvalidRequestError(
                err.get('message'), err.get('param'), rbody, rcode, resp)
        elif rcode == 401:
            raise error.AuthenticationError(
                err.get('message'), rbody, rcode, resp)
        elif rcode == 402:
            raise error.CardError(err.get('message'), err.get('param'),
                                  err.get('code'), rbody, rcode, resp)
        else:
            raise error.APIError(err.get('message'), rbody, rcode, resp)

    def request_raw(self, method, url, params=None):
        """
        Mechanism for issuing an API call
        """
        from pingpp import api_version

        if self.api_key:
            my_api_key = self.api_key
        else:
            from pingpp import api_key
            my_api_key = api_key

        if my_api_key is None:
            raise error.AuthenticationError(
                'No API key provided. (HINT: set your API key using '
                '"pingpp.api_key = <API-KEY>"). You can generate API keys '
                'from the Ping++ web interface.  See https://pingplusplus.com '
                'for details, or email support@pingplusplus.com if you have any '
                'questions.')

        abs_url = '%s%s' % (pingpp.api_base, url)

        encoded_params = urllib.urlencode(list(_api_encode(params or {})))

        if method == 'get' or method == 'delete':
            if params:
                abs_url = _build_api_url(abs_url, encoded_params)
            post_data = None
        elif method == 'post':
            post_data = encoded_params
        else:
            raise error.APIConnectionError(
                'Unrecognized HTTP method %r.  This may indicate a bug in the '
                'Ping++ bindings.  Please contact support@pingplusplus.com for '
                'assistance.' % (method,))

        ua = {
            'bindings_version': version.VERSION,
            'lang': 'python',
            'publisher': 'pingpp',
            'httplib': self._client.name,
        }
        for attr, func in [['lang_version', platform.python_version],
                           ['platform', platform.platform],
                           ['uname', lambda: ' '.join(platform.uname())]]:
            try:
                val = func()
            except Exception, e:
                val = "!! %s" % (e,)
            ua[attr] = val

        headers = {
            'X-Pingpp-Client-User-Agent': util.json.dumps(ua),
            'User-Agent': 'Pingplusplus/v1 PythonBindings/%s' % (version.VERSION,),
            'Authorization': 'Bearer %s' % (my_api_key,)
        }

        if method == 'post':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        if api_version is not None:
            headers['Pingplusplus-Version'] = api_version

        rbody, rcode = self._client.request(
            method, abs_url, headers, post_data)

        util.logger.info(
            'API request to %s returned (response code, response body) of '
            '(%d, %r)',
            abs_url, rcode, rbody)
        return rbody, rcode, my_api_key

    def interpret_response(self, rbody, rcode):
        try:
            if hasattr(rbody, 'decode'):
                rbody = rbody.decode('utf-8')
            resp = util.json.loads(rbody)
        except Exception:
            raise error.APIError(
                "Invalid response body from API: %s "
                "(HTTP response code was %d)" % (rbody, rcode),
                rbody, rcode)
        if not (200 <= rcode < 300):
            self.handle_api_error(rbody, rcode, resp)
        return resp

    def _check_ssl_cert(self):
        """Preflight the SSL certificate presented by the backend.

        This isn't 100% bulletproof, in that we're not actually validating the
        transport used to communicate with Ping++, merely that the first
        attempt to does not use a revoked certificate.

        Unfortunately the interface to OpenSSL doesn't make it easy to check
        the certificate before sending potentially sensitive data on the wire.
        This approach raises the bar for an attacker significantly."""

        from pingpp import verify_ssl_certs

        if verify_ssl_certs and not self._CERTIFICATE_VERIFIED:
            uri = urlparse.urlparse(pingpp.api_base)
            try:
                certificate = ssl.get_server_certificate(
                    (uri.hostname, uri.port or 443), ssl_version=3)
                der_cert = ssl.PEM_cert_to_DER_cert(certificate)
            except socket.error, e:
                raise error.APIConnectionError(e)
            except TypeError:
                # The Google App Engine development server blocks the C socket
                # module which causes a type error when using the SSL library
                if util.is_appengine_dev():
                    self._CERTIFICATE_VERIFIED = True
                    warnings.warn(
                        'We were unable to verify Ping++\'s SSL certificate '
                        'due to a bug in the Google App Engine development '
                        'server. Please alert us immediately at '
                        'support@pingplusplus.com if this message appears in your '
                        'production logs.')
                    return
                else:
                    raise
            self._CERTIFICATE_VERIFIED = certificate_blacklist.verify(der_cert)

    # Deprecated request handling.  Will all be removed in 2.0
    def _deprecated_request(self, impl, method, url, headers, params):
        warnings.warn(
            'The *_request functions of APIRequestor are deprecated and '
            'will be removed in version 2.0. Please use the client classes '
            ' in `pingpp.http_client` instead',
            DeprecationWarning, stacklevel=2)

        method = method.lower()

        if method == 'get' or method == 'delete':
            if params:
                url = self.build_url(url, params)
            post_data = None
        elif method == 'post':
            post_data = self.encode(params)
        else:
            raise error.APIConnectionError(
                'Unrecognized HTTP method %r.  This may indicate a bug in the '
                'Ping++ bindings.  Please contact support@pingplusplus.com for '
                'assistance.' % (method,))

        client = impl(verify_ssl_certs=self._client._verify_ssl_certs)
        return client.request(method, url, headers, post_data)

    def _deprecated_handle_error(self, impl, *args):
        warnings.warn(
            'The handle_*_error functions of APIRequestor are deprecated and '
            'will be removed in version 2.0. Please use the client classes '
            ' in `pingpp.http_client` instead',
            DeprecationWarning, stacklevel=2)

        client = impl(verify_ssl_certs=self._client._verify_ssl_certs)
        return client._handle_request_error(*args)

    def requests_request(self, meth, abs_url, headers, params):
        from pingpp.http_client import RequestsClient
        return self._deprecated_request(RequestsClient, meth, abs_url,
                                        headers, params)

    def handle_requests_error(self, err):
        from pingpp.http_client import RequestsClient
        return self._deprecated_handle_error(RequestsClient, err)

    def pycurl_request(self, meth, abs_url, headers, params):
        from pingpp.http_client import PycurlClient
        return self._deprecated_request(PycurlClient, meth, abs_url,
                                        headers, params)

    def handle_pycurl_error(self, err):
        from pingpp.http_client import PycurlClient
        return self._deprecated_handle_error(PycurlClient, err)

    def urlfetch_request(self, meth, abs_url, headers, params):
        from pingpp.http_client import UrlFetchClient
        return self._deprecated_request(UrlFetchClient, meth, abs_url,
                                        headers, params)

    def handle_urlfetch_error(self, err, abs_url):
        from pingpp.http_client import UrlFetchClient
        return self._deprecated_handle_error(UrlFetchClient, err, abs_url)

    def urllib2_request(self, meth, abs_url, headers, params):
        from pingpp.http_client import Urllib2Client
        return self._deprecated_request(Urllib2Client, meth, abs_url,
                                        headers, params)

    def handle_urllib2_error(self, err, abs_url):
        from pingpp.http_client import Urllib2Client
        return self._deprecated_handle_error(Urllib2Client, err)
