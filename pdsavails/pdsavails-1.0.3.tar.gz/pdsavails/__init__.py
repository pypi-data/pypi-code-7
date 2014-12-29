#!/usr/bin/env python

import os
import requests
from datetime import datetime
import time
import hmac
import hashlib
import socket
import urllib
try:
    import json
except ImportError:
    import simplejson as json

API_VERSION = 'api/v1.0/'
DEFAULT_BASE_URL = 'https://avails.premieredigital.net/'
# DEFAULT_BASE_URL = 'http://localhost:8000/' # Uncomment for development



class PDSAvailsError(Exception):
    pass # TODO



class PDSAvails(object):

    def __init__(self, api_key=None, api_pass=None, base_url=None, skip_credentials=False):
	
        if not base_url:
            base_url = os.path.join(DEFAULT_BASE_URL, API_VERSION)

        if not skip_credentials:
            if not api_key:
                try:
                    api_key = os.environ['PDSAVAILS_ACCESS_KEY']
                except KeyError:
                    raise PDSAvailsError('PDSAVAILS_ACCESS_KEY not set.')
            
            if not api_pass:
                try:
                    api_pass = os.environ['PDSAVAILS_ACCESS_PASSWORD']
                except KeyError:
                    raise PDSAvailsError('PDSAVAILS_ACCESS_PASSWORD not set.')

        self.base_url = base_url
        self.api_key = api_key
        self.api_pass = api_pass


    def _build_request(self, url, method, data=None):
        """
        The signature is a concatenation of nonce + url + body.
        `method` must be one of 'GET', 'POST', 'PUT', or 'DELETE'.
        """
        if not url:
            raise PDSAvailsError('A url must be specified.')
        
        nonce = str(int(time.time() * 1e6))
        if data:
            body = json.dumps(data)
        else:
            body = ''

        message = nonce + url + body
        signature = hmac.new(self.api_pass, message, hashlib.sha256).hexdigest()
        headers = {
            'Access-Key': self.api_key,
            'Access-Signature': signature,
            'Access-Nonce': nonce,
            'Content-Type': 'application/json',
        }
            
        if method == 'GET':
            r = requests.get(url, headers=headers)
        elif method == 'POST':
            r = requests.post(url, headers=headers, data=body)
        elif method == 'PUT':
            r = requests.put(url, headers=headers, data=body)
        elif method == 'DELETE':
            r = requests.delete(url, headers=headers)
        
        try:
            r_data = r.json()
        except: # most likely a JSONDecodeError
            raise PDSAvailsError(r)
        
        return r_data


    def validate_credentials(self):
        '''
        Test method to validate user's Credentials.
        '''
        method_type = 'GET'
        method_path = 'validate/'
        url = os.path.join(self.base_url, method_path)

        return self._build_request(url, method_type)


if __name__ == '__main__':
    
    # Quicker to test this way than with Python tests.
    KEY = '58178a3b56814f9d'
    PASS = '73f253a65db94cd3'
    avails = PDSAvails(KEY, PASS)
    
    
    r = avails.validate_credentials()
    print '>>>', r





        