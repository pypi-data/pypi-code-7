#!/usr/bin/env python
#
#
# @author <a href="hoang281283@gmail.com">Minh Hoang TO</a>
# @date: 12/22/14
#
#
# ==============================================================

from hashlib import sha1
import hmac
import base64

import requests


baseURL = 'http://s3.cloudbase.vn/api/v1'


def gen_signature(access_key_id, access_key_value, random_data):
    data_to_signed = access_key_id + ":" + random_data
    hashed = hmac.new(access_key_value, data_to_signed, sha1)
    encode_hashed = base64.b64encode(hashed.digest())

    return data_to_signed + ":" + encode_hashed


class ApiCaller:
    def __init__(self, params):
        if params['signature'] is not None:
            self.signature = params['signature']
        else:
            key_id = params['access_key_id']
            key_value = params['access_key_value']
            random_data = "abcdefgh" if params['random_data'] is None else params['random_data']
            self.signature = gen_signature(key_id, key_value, random_data)

    def do_get(self, path, headers={}):
        headers['Authorization'] = self.signature
        return requests.get(url=baseURL + path, headers=headers)

    def do_post(self, path, payload=None, headers={}):
        headers['Authorization'] = self.signature
        return requests.post(url=baseURL + path, data=payload, headers=headers)

    def do_put(self, path, payload=None, headers={}):
        headers['Authorization'] = self.signature
        return requests.put(url=baseURL + path, data=payload, headers=headers)

    def do_delete(self, path, headers={}):
        headers['Authorization'] = self.signature
        return requests.delete(url=baseURL + path, headers=headers)

    def do_get_to_obj(self, path, headers={}, unmarshaller=None):
        headers['Authorization'] = self.signature
        res = requests.get(url=baseURL + path, headers=headers)
        return res if unmarshaller is None else unmarshaller(res)

    def do_post_to_obj(self, path, payload=None, headers={}, unmarshaller=None):
        headers['Authorization'] = self.signature
        res = requests.post(url=baseURL + path, data=payload, headers=headers)
        return res if unmarshaller is None else unmarshaller(res)

    def do_put_to_obj(self, path, payload=None, headers={}, unmarshaller=None):
        headers['Authorization'] = self.signature
        res = requests.put(url=baseURL + path, data=payload, headers=headers)
        return res if unmarshaller is None else unmarshaller(res)

    def do_delete_to_obj(self, path, headers={}, unmarshaller=None):
        headers['Authorization'] = self.signature
        res = requests.delete(url=baseURL + path, headers=headers)
        return res if unmarshaller is None else unmarshaller(res)






