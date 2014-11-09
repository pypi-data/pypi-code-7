__all__ = ['PyClient', 'WsgiClient', 'HttpClient']

from base64 import b64encode, b64decode
from time import time as timestamp
from os.path import join
from cxor import xor
import scrypt

from _crypto import (
    nacl_nonce, nacl_random, nacl_box, nacl_sign, nacl_sha256, nacl_verify,
    Box, PrivateKey, PublicKey, VerifyKey, SigningKey,
)
from _term import Hict, parse_term, parse_json, to_simple, to_json
from _service import consume, prelogin, login, logout, gen_pad
import _exc as exc


class PyClient(object):
    """Python client

    The easy way to locally consume encrypted services from python programs.
    Mostly usefull during development and testing.
    """
    urlpaths = Hict(prelogin=prelogin.urlpath,
                    login=login.urlpath,
                    logout=logout.urlpath,
                    gen_pad=gen_pad.urlpath)
    password = Hict(hash_func=scrypt.hash)

    def __init__(self, **state):
        from _state import get_state
        self._state = get_state(**state)

    def _consume(self, urlpath, **argd):
        _, ext, ret = consume(self._state, urlpath, **argd)
        return ret

    def _build_urlpath(self, urlpath, args):
        if args:
            urlpath, ext = splitext(urlpath)
            urlpath = join(urlpath, *args) + ext
        return urlpath

    def login(self, login, password, force=False, **argd):
        urlpaths = self.urlpaths
        # prelogin
        ret = Hict(self._consume(urlpaths.prelogin, identity=login, **argd))
        password_hash = self.password.hash_func(password, b64decode(ret.salt))
        box, _, _ = nacl_box(b64decode(ret.pkey), nacl_sha256(password_hash))
        try:
            msg = box.decrypt(b64decode(ret.enc))
        except:
            raise exc.InvalidCredential(login, self._state)
        # login
        sid = b64encode(msg[64:80])
        cseed, vkey, pad = msg[:32], msg[32:64], msg[80:]
        sign, _ = nacl_sign(password_hash, cseed)
        ret = Hict(self._consume(urlpaths.login, identity=login, sid=sid,
                                 sign=b64encode(xor(sign[:64], pad)),
                                 force=force))
        msg = box.decrypt(nacl_verify(b64decode(ret.sign), vkey))
        self._auth = Hict(sid=sid,
                          tdiff=int(msg[64:]) - timestamp(),
                          sign_key=SigningKey(cseed),
                          verify_key=VerifyKey(vkey),
                          box=Box(PrivateKey(msg[:32]), PublicKey(msg[32:64])))
        return True

    def call(self, urlpath, *args, **argd):
        return self._consume(self._build_urlpath(urlpath, args), **argd)

    def safe_call(self, urlpath, *args, **argd):
        # get one-time-pad and one-time-keys
        auth = self._auth
        box = auth.box
        params = to_json(to_simple(argd))
        size = len(params) + 40
        pad = nacl_random(size + 410)
        msg = to_json(dict(call=urlpath, pad=b64encode(pad),
                           tstamp=int(timestamp()) + auth.tdiff))
        enc = box.encrypt(msg, nacl_nonce())
        sign = b64encode(auth.sign_key.sign(enc))
        ret = self._consume(self.urlpaths.gen_pad, sid=auth.sid, sign=sign)
        enc = auth.verify_key.verify(b64decode(ret['sign']))
        assert len(enc) < len(pad), (len(enc), len(pad))
        cpad = Hict(parse_json(box.decrypt(xor(enc, pad))))
        # build real request
        box, _, _ = nacl_box(b64decode(cpad.skey), b64decode(cpad.ckey))
        enc = xor(box.encrypt(params, nacl_nonce()), b64decode(cpad.pad))
        sign = b64encode(SigningKey(b64decode(cpad.cseed)).sign(enc))
        ret = self._consume(urlpath, sid=auth.sid, pid=cpad.pid, sign=sign)
        enc = VerifyKey(b64decode(cpad.vkey)).verify(b64decode(ret['sign']))
        return parse_json(box.decrypt(enc))

    def logout(self):
        return self.safe_call(self.urlpaths.logout)


from _wsgi import handler as wsgi_app
from os.path import splitext
from webob import Request
import requests


class WsgiClient(PyClient):

    def _parse_response(self, status, body):
        try:
            if status == 200:
                return parse_term(parse_json(body))
            else:
                error = Hict(parse_json(body))
        except:
            return body

        try:
            exc_class = (getattr(exc, error.exc, None) or
                         getattr(__builtins__, error.exc))
        except:
            return body

        raise exc_class(*error.err)

    def _consume(self, urlpath, **argd):
        params = dict((k, (v.name, v) if isinstance(v, file) else v)
                      for k, v in argd.iteritems()) if argd else None

        _, ext = splitext(urlpath)
        if not ext:
            urlpath = urlpath + '.json'

        if urlpath.endswith('.json'):
            params = dict(_json_=to_json(to_simple(params)))

        schema = 'https' if self._state.ssl is True else 'http'
        base_url = '%s://%s' % (schema, self._state.domain)
        req = Request.blank(urlpath, base_url=base_url, POST=params)
        req.headers['X-Fanery-Call'] = 'true'

        res = req.get_response(wsgi_app)
        return self._parse_response(res.status_int, res.body)


class HttpClient(WsgiClient):

    def __init__(self, host='127.0.0.1', port=9000, **argd):
        super(HttpClient, self).__init__(**argd)
        scheme = 'http' if not self._state.ssl else 'https'
        self.__baseurl = '%s://%s:%s' % (scheme, host, port)

    def _consume(self, urlpath, **argd):
        url = '/'.join((self.__baseurl, urlpath))

        _, ext = splitext(url)
        if not ext:
            url = url + '.json'

        if argd:
            data, files = dict(), dict()

            for k, v in argd.iteritems():
                if isinstance(v, file):
                    files[k] = v
                else:
                    data[k] = v

            if url.endswith('.json'):
                data = dict(_json_=to_json(to_simple(data)))

            res = requests.post(url, files=files, data=data)

        else:
            res = requests.get(url)

        return self._parse_response(res.status_code, res.content)
