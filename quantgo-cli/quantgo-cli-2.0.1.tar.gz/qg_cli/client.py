# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

import datetime
import logging
import os
import platform
import requests
import sys

from qg_cli import __version__

from urllib import urlencode

from signatures import Sigv2
from api_schema import commands
from errors import InvalidAction, ServerError

ENDPOINT = 'https://quantgo.com:8443/'
API_ROUTE = 'api'
SIGNATURE_METHOD = 'HmacSHA256'
SIGNATURE_VERSION = '2'
ISO_UTC_NOW = lambda: datetime.datetime.utcnow().isoformat()
API_VERSION = '1.0'
PY_VERSION = sys.version.split()[0]
PLATFORM = ':'.join(platform.uname())


class ApiClient(object):
    def __init__(self, access_key=None, secret_key=None):
        """Create and init client instance"""
        self.url = os.path.join(ENDPOINT, API_ROUTE)
        self.access_key = access_key
        self.secret_key = secret_key
        self.signature_provider = Sigv2
        self.method = 'POST'
        self.headers = {}
        self.request = None
        self.commands = commands
        self.user_agent = 'quantgo-cli/Version %s/Python v%s/%s' % (
            __version__, PY_VERSION, PLATFORM)

    def _prepare_params_dict(self, params):
        result = []
        for k, vs in list(params.items()):
            if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                vs = [vs]
            for v in vs:
                if v is not None:
                    result.append(
                        (k.encode('utf-8') if isinstance(k, str) else k,
                         v.encode('utf-8') if isinstance(v, str) else v))
        return urlencode(result, doseq=True)

    def add_auth(self):
        """Add auth headers to request."""
        if not all((self.access_key, self.secret_key)):
            raise Exception('You must set credentials before using client.')

        self.request.params['AccessKeyId'] = self.access_key
        self.request.params['SignatureVersion'] = SIGNATURE_VERSION
        self.request.params['SignatureMethod'] = SIGNATURE_METHOD
        self.request.params['Timestamp'] = ISO_UTC_NOW()
        self.request.params['Version'] = API_VERSION
        full_url = '%s?%s' % (self.request.url,
                              self._prepare_params_dict(self.request.params))
        logging.debug(full_url)
        signature = self.signature_provider(self.access_key,
                self.secret_key).calculate(self.method, full_url)

        self.request.params['Signature'] = signature

    def set_credentials(self, access_key, secret_key):
        """Allows to set credentials."""
        self.access_key = access_key
        self.secret_key = secret_key

    @property
    def get_credentials(self):
        """Return credentials dict."""
        return dict(access_key=self.access_key, secret_key=self.secret_key)

    def _prepare_headers(self):
        """Make additional preparations."""
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
        self.headers['User-Agent'] = self.user_agent

    def call(self, action_name, **params):
        logging.debug(params)
        action = self.commands.get(action_name)
        if action is None:
            raise InvalidAction(
                'Action %s is not valid quantgo action.' % (action_name,))
        self.params = {'Action': action['name']}
        self.params.update(params)
        self._prepare_headers()
        sess = requests.Session()
        self.request = requests.Request(self.method,
                                        self.url,
                                        params=self.params,
                                        headers=self.headers)
        self.add_auth()
        prepared = self.request.prepare()
        response = sess.send(prepared)
        if not response.status_code == 200:
            raise ServerError(
                'Request failed: server returned status %s. Reason: %s' \
                 % (response.status_code, response.content))
        return response.content
