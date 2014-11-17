# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""plugin authentication retriever

:organization: Logilab
:copyright: 2010-2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

__docformat__ = "restructuredtext en"

import hashlib
from datetime import datetime, timedelta
from email.utils import parsedate
from functools import partial
from itertools import imap as map

from cubicweb import AuthenticationError
from cubicweb.predicates import is_instance
from cubicweb.web.views.authentication import NoAuthInfo
try:
    from cubicweb.web.views.authentication import WebAuthInfoRetriever
except ImportError:
    # old typo, now fixed but we want to be compatible with 3.15
    from cubicweb.web.views.authentication import WebAuthInfoRetreiver as WebAuthInfoRetriever


# web authentication info retriever ############################################

class HttpRESTAuthRetriever(WebAuthInfoRetriever):
    """Authenticate by the Authorization http header """
    __regid__ = 'www-authorization'
    headers_to_sign = ('Content-MD5', 'Content-Type', 'Date')
    order = 0

    def authentication_information(self, req):
        """retrieve authentication information from the given request, raise
        NoAuthInfo if expected information is not found
        return token id, signed string and signature
        """
        self.debug('web authenticator building auth info')
        login, signature = self.parse_authorization_header(req)
        string_to_sign = self.build_string_to_sign(req)
        return login, {'signature': signature, 'request': string_to_sign}

    def build_string_to_sign(self, req):
        """Return the string used to authenticate the request.

        The client must have provided a signed version of this string.

        The string is the concatenation of the http verb, url and values of the
        http request header fields specified in ``headers_to_sign``.
        """
        get_header = lambda field: req.get_header(field, '')
        return req.http_method() + req.url() + ''.join(map(get_header, self.headers_to_sign))

    def parse_authorization_header(self, req):
        """Return the token id and the request signature.

        They are retrieved from the http request headers "Authorization"
        """
        header = req.get_header('Authorization', None)
        if header is None:
            self.debug('SIGNED REQUEST: error header is none')
            raise NoAuthInfo()
        try:
            method, credentials = header.split(None, 1)
        except ValueError:
            self.debug("SIGNED REQUEST: couldn't determine method from Authorization header")
            raise NoAuthInfo()
        if method != 'Cubicweb':
            self.debug('SIGNED REQUEST: method not cubicweb')
            raise NoAuthInfo() # XXX NoAuthInfo ??
        if req.http_method() != 'GET':
            try:
                content = req.content
            except AttributeError:
                # XXX cw 3.15 compat
                content = req._twreq.content
            md5 = hashlib.md5()
            content.seek(0)
            while True:
                data = content.read(4096)
                if not data:
                    break
                md5.update(data)
            if md5.hexdigest() != req.get_header('Content-MD5'):
                self.debug('SIGNED REQUEST: wrong md5, %s != %s' % (md5.hexdigest(), req.get_header('Content-MD5')))
                raise AuthenticationError()
            content.seek(0)
        date_header = req.get_header('Date')
        if date_header is None:
            raise AuthenticationError()
        try:
            date = datetime(*parsedate(date_header)[:6])
        except (ValueError, TypeError):
            self.debug('SIGNED REQUEST: wrong date format')
            raise AuthenticationError()
        delta = datetime.utcnow() - date
        if delta < timedelta(0) or delta > timedelta(0, 300):
            self.debug('SIGNED REQUEST: date delta error')
            raise AuthenticationError()

        try:
            id, signature = credentials.split(':', 1)
            self.debug('encoding info for %s' % id)
            return id, signature
        except Exception, exc:
            self.exception('HTTP REST authenticator failed')
            raise NoAuthInfo()

    def request_has_auth_info(self, req):
        signature = req.get_header('Authorization', None)
        return signature is not None

    def revalidate_login(self, req):
        return None

    def cleanup_authentication_information(self, req):
        # we found our header, but authentication failed; we don't want to fall
        # back to other retrievers or (especially) an anonymous login
        raise AuthenticationError()

# Tokens managment #############################################################


from cubicweb.web.views import uicfg

_afs = uicfg.autoform_section
_pvs = uicfg.primaryview_section
_rctrl = uicfg.reledit_ctrl
_affk = uicfg.autoform_field_kwargs
_pvdc = uicfg.primaryview_display_ctrl
_afs.tag_attribute(('AuthToken', 'token'), 'main', 'hidden')
_afs.tag_subject_of(('AuthToken', 'token_for_user', 'CWUser'), 'main', 'hidden')
_pvs.tag_subject_of(('AuthToken', 'token_for_user', 'CWUser'), 'hidden')
_rctrl.tag_attribute(('AuthToken', 'id'), {'reload': True})
_affk.tag_attribute(('AuthToken', 'id'), {'required': False})
_pvdc.tag_attribute(('AuthToken', 'token'), {'vid': 'verbatimattr'})


