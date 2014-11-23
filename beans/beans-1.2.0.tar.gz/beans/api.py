import sys
import json
from .exception import BeansException


class Beans(object):

    signature = 'My Python App v0'  # Set this value to whatever the SDK is used for
    fail_silently = True
    logger = None

    endpoint = 'http://api.beans.cards/v1/'
    access_token_path = 'oauth/access_token'

    version = ''

    def __init__(self, secret, logger=None, fail_silently=True, signature='My Python App v0'):
        self.__secret__ = secret
        self.logger = logger
        self.fail_silently = fail_silently
        self.signature = signature

    def get(self, path, fail_silently=None, **kwargs):
        return self.make_request('GET', path, data=kwargs, fail_silently=fail_silently)

    def post(self, path, fail_silently=None, **kwargs):
        return self.make_request('POST', path, data=kwargs, fail_silently=fail_silently)

    def delete(self, path, fail_silently=None, **kwargs):
        return self.make_request('DELETE', path, data=kwargs, fail_silently=fail_silently)

    def get_token_from_cookie(self, cookies, fail_silently=None):

        code = cookies.get('beans_user')
        if code:
            return self.get(self.access_token_path, fail_silently=fail_silently, code=code)

    def make_request(self, method, path, data=None, fail_silently=None):

        url = self.endpoint + path

        ua = {
            'bindings_version': self.version,
            'application':      self.signature,
            'lang':             'PHP',
            'lang_version':     sys.version,
            'publisher':        'Beans',
        }

        headers = {
            'X-Beans-Client-User-Agent':    json.dumps(ua),
        }

        import requests
        response = requests.request(method, url, auth=(self.__secret__, ''),
                                    headers=headers, json=data, timeout=80)

        r = json.loads(response.content.decode('utf-8'))

        if r['error']:
            self.handle_error(r['error'], fail_silently)
        else:
            return r['result']

    def handle_error(self, error_str, fail_silently=None):

        if fail_silently is None:
            fail_silently = self.fail_silently

        error = BeansException(error_str)

        if fail_silently and self.logger:

            self.logger.exception('[Beans]: '+str(error))
            return None

        else:
            raise error
