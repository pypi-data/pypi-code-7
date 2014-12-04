# -*- coding: utf-8 -*-
from google.appengine.api import memcache
CACHE_SIZE = 900000
FORMAT_KEY_NAME = '%s_split_%d'
FORMAT_KEY_COUNT = '%s_split_count'

'''
memcache 커스터마이징
자동으로 최대 캐시 크기만큼 split해서 저장/리턴 해준다
'''

def set(key, value, namespace=None):
    data = value
    count = 0
    while len(value) > 0:
        cur_data = data[0:CACHE_SIZE]
        data = data[CACHE_SIZE:]
        cur_key_name = FORMAT_KEY_NAME % (key, count)
        memcache.set(namespace=namespace, key=cur_key_name, value=cur_data)
        count += 1
    cur_key_count = FORMAT_KEY_COUNT % (key)
    memcache.set(namespace=namespace, key=cur_key_count, value=count)
    return True
    # try:
    #     data = value
    #     count = 0
    #     while len(value) > 0:
    #         cur_data = data[0:CACHE_SIZE]
    #         data = data[CACHE_SIZE:]
    #         cur_key_name = FORMAT_KEY_NAME % (key, count)
    #         memcache.set(namespace=namespace, key=cur_key_name, value=cur_data)
    #         count += 1
    #     cur_key_count = FORMAT_KEY_COUNT % (key)
    #     memcache.set(namespace=namespace, key=cur_key_count, value=count)
    #     return True
    # except Exception as e:
    #     print type(e)
    #     print e.args
    #     print e
    #     return False

def get(key, namespace=None):
    cur_key_count = FORMAT_KEY_COUNT % (key)
    count = memcache.get(namespace=namespace, key=cur_key_count)

    if count is None:
        return None

    data_combine = ''
    for i in range(count):
        cur_key_name = FORMAT_KEY_NAME % (key, count)
        cur_data = memcache.get(namespace=namespace, key=cur_key_name)

        if cur_data is None:
            return None
        data_combine += cur_data
    return data_combine