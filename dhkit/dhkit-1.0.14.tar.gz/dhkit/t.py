# coding:utf8

"""
Created on 2014-11-21

@author: tufei
@description:
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
from cache import Cacheable

c = Cacheable()

@c.cacheable()
def get_name(usercode):
    return 'name: %s' % usercode


def update_name(usercode):
    c.delete_cache(get_name, usercode)
    return get_name(usercode)


if __name__ == '__main__':
    # import time
    # print get_name('123456')
    # time.sleep(30)
    # print get_name('123457')
    # time.sleep(30)
    # print get_name('123458')
    # time.sleep(30)
    # print get_name('123459')
    #update_name('123456')
    c.delete_cache(get_name, '123456')