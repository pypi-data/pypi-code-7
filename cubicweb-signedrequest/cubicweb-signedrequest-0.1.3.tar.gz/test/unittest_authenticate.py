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

"""cubicweb-signedrequest automatic tests for authentication
"""
import hmac
from email.utils import formatdate
from operator import itemgetter
import time
from StringIO import StringIO

from cubicweb.devtools.testlib import CubicWebTC, real_error_handling
from cubicweb.web.controller import Controller

HEADERS_TO_SIGN = ('Content-MD5', 'Content-Type', 'Date')

class TestController(Controller):
    __regid__ = 'testauth'

    def publish(self, rset):
        if self._cw.user.login == self._cw.form.get('expected', 'admin'):
            return u'VALID'
        else:
            return u'INVALID'


class TrustedAuthTC(CubicWebTC):

    def setup_database(self):
        req = self.request()
        req.execute('INSERT AuthToken T: T token "my precious", '
                    '                    T token_for_user U, '
                    '                    T id "admin", '
                    '                    T enabled True'
                    ' WHERE U login "admin"')

    def _build_string_to_sign(self, headers, method='GET', data=None, files=None, **params):
        get_headers = itemgetter(*HEADERS_TO_SIGN)
        url = self.request().build_url(TestController.__regid__)
        return method + url + ''.join(get_headers(headers))

    def _build_signature(self, id, string_to_sign):
        req = self.request()
        rset = req.execute('Any K WHERE T id %(id)s, T token K',
                           {'id': id})
        assert rset
        return hmac.new(str(rset[0][0]), string_to_sign).hexdigest()

    def _test_header_format(self, method, login, signature, http_method='GET',
                            headers=None, content=None, **params):
        if headers is None:
            headers = {}
        with self.temporary_appobjects(TestController):
            url = params.pop('url', TestController.__regid__)
            req = self.requestcls(self.vreg, url=url,
                                  method=http_method, **params)
            req.form['expected'] = 'admin'
            # Fill an arbitrary body content if POST.
            if http_method == 'POST':
                if content is None:
                    content = "rql=Any+X+WHERE+X+is+Player"
                req.content = StringIO(content)
            req.set_request_header('Authorization', '%s %s:%s' % (method, login, signature), raw=True)
            for name, value in headers.items():
                req.set_request_header(name, value, raw=True)
            with real_error_handling(self.app):
                result = self.app.handle_request(req, 'testauth')
        return result, req

    def get_valid_authdata(self, headers=None):
        if headers is None:
            headers = {}
        headers.setdefault('Content-MD5', 'aa3d66a90f73242ef6f679ce26b3691e')
        headers.setdefault('Content-Type', 'application/xhtml+xml')
        headers.setdefault('Date', formatdate(usegmt=True))
        string_to_sign = self._build_string_to_sign(headers)
        signature = self._build_signature('admin', string_to_sign)
        return signature, headers

    def test_login(self):
        signature, headers = self.get_valid_authdata()
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               signature=signature,
                                               headers=headers)
        self.assertEqual(200, req.status_out)
        self.assertEqual('VALID', result)

    def test_bad_date(self):
        for date in (formatdate(time.time() + 1000, usegmt=True),
                     formatdate(time.time() - 1000, usegmt=True),
                     'toto'):
            headers = {'Date': date}
            signature, headers = self.get_valid_authdata(headers)
            result, req = self._test_header_format(method='Cubicweb',
                                                   login='admin',
                                                   signature=signature,
                                                   headers=headers)
            self.assertGreater(req.status_out, 400)

    def test_bad_http_auth_method(self):
        signature = self._build_signature('admin', '')
        result, req = self._test_header_format(method='AWS', login='admin', signature=signature)
        self.assertEqual(req.status_out, 200)
        self.assertEqual(req.user.login, 'anon')

    def test_bad_signature(self):
        result, req = self._test_header_format(method='Cubicweb', login='admin', signature='YYY')
        self.assertGreater(req.status_out, 400)

    def test_deactivated_token(self):
        req = self.request()
        req.execute('SET T enabled False WHERE T token_for_user U, U login %(l)s',
                    {'l':'admin'})
        self.commit()
        signature, headers = self.get_valid_authdata()
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               signature=signature,
                                               headers=headers)
        self.assertGreater(req.status_out, 400)

    def test_bad_signature_url(self):
        def bad_build_string_to_sign(self, headers):
            get_headers = itemgetter(*HEADERS_TO_SIGN)
            return ''.join(get_headers(headers))
        self._build_string_to_sign = bad_build_string_to_sign
        result, req = self._test_header_format(method='Cubicweb', login='admin', signature='YYY')
        self.assertGreater(req.status_out, 400)


    def test_post_http_request_signature(self):
        headers = {'Content-MD5': '43115f65c182069f76b56df967e5c3fd',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Date': formatdate(usegmt=True)}
        string_to_sign = self._build_string_to_sign(headers, method='POST')
        signature = self._build_signature('admin', string_to_sign)
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               signature=signature,
                                               http_method='POST',
                                               headers=headers)
        self.assertEqual(200, req.status_out)
        self.assertEqual('VALID', result)

    def test_post_http_request_signature_with_multipart(self):
        date = formatdate(usegmt=True)
        headers = {'Content-MD5': 'f47787068b27ee123d28392f2d21cf70',
                   'Content-Type': 'multipart/form-data; boundary=a71da6eca73a45459439dd288f8185a4',
                   'Date': date}
        string_to_sign = 'POSThttp://testing.fr/cubicweb/testauth?key1=value1f47787068b27ee123d28392f2d21cf70multipart/form-data; boundary=a71da6eca73a45459439dd288f8185a4%s' % date
        body = '--a71da6eca73a45459439dd288f8185a4\r\nContent-Disposition: form-data; name="datak1"\r\n\r\nsome content\r\n--a71da6eca73a45459439dd288f8185a4\r\nContent-Disposition: form-data; name="filename"; filename="filename"\r\nContent-Type: application/octet-stream\r\n\r\nabc\r\n--a71da6eca73a45459439dd288f8185a4--\r\n'
        signature = self._build_signature('admin', string_to_sign)
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               content=body,
                                               signature=signature,
                                               http_method='POST',
                                               headers=headers,
                                               url='http://testing.fr/cubicweb/testauth?key1=value1'
                                               )
        self.assertEqual(200, req.status_out)
        self.assertEqual('VALID', result)


    def test_post_http_request_signature_with_data(self):
        date = formatdate(usegmt=True)
        headers = {'Content-MD5': '9893532233caff98cd083a116b013c0b',
                   'Date': date}
        string_to_sign = 'POSThttp://testing.fr/cubicweb/testauth?key1=value19893532233caff98cd083a116b013c0b%s' % date
        body = 'some content'
        signature = self._build_signature('admin', string_to_sign)
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               content=body,
                                               signature=signature,
                                               http_method='POST',
                                               headers=headers,
                                               url='http://testing.fr/cubicweb/testauth?key1=value1'
                                               )
        self.assertEqual(200, req.status_out)
        self.assertEqual('VALID', result)


if __name__ == "__main__":
    from logilab.common.testlib import unittest_main
    unittest_main()
