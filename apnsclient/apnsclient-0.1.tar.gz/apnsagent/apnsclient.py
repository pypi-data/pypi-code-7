# encoding=utf-8

import time
import hashlib
import requests
import simplejson
from datetime import datetime

HEADER_API_KEY = 'X-APNSAGENT-API-KEY'
HEADER_API_VERSION = 'X-APNSAGENT-API-VERSION'
HEADER_API_SIGNATURE = 'X-APNSAGENT-API-SIGNATURE'
HEADER_API_TS = 'X-APNSAGENT-API-TIMESTAMP'

push_url = '%s/api/push/'

class PushClient(object):

    def __init__(self, app_key, app_secret, host='http://apns.sutui.me'):
        self.app_key = app_key
        self.app_secret = app_secret
        self.host = host

    def send_request(self, url, params, method='GET'):
        
        timestamp = str(time.time())
        sign_str = '%s&%s&%s' % (self.app_key, self.app_secret, timestamp)
        signature = hashlib.sha1(sign_str).hexdigest()

        headers = {HEADER_API_KEY: self.app_key,
                   HEADER_API_SIGNATURE: signature,
                   HEADER_API_TS: timestamp}
        
        params = simplejson.dumps(params)
        
        if method.lower() == 'get':
            result = requests.get(url, params={'data':params}, headers=headers)
        elif method.lower() == 'post':
            result = requests.post(url, data={'data':params}, headers=headers)
        else:
            raise Exception(u'unknow http method %s' % method)
        try:
            return simplejson.loads(result.text)
        except:
            return result.text


    def push(self, user_id, message, badge=0, sound='default', custom={}):
        
        params = []
        params.append({'user_id': user_id,
                  'message': message,
                  'badge': badge,
                  'sound': sound,
                  'custom': custom})
                  
        return self.send_request(push_url % self.host, params, 'POST')
    
    
