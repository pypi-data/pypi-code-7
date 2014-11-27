# coding:utf8

"""
Created on 2014-11-21

@author: tufei
@description:
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import logging.handlers
import tornado.tcpserver
import functools

def wrapper(func):
    @functools.wraps(func)
    def _warpper(*args, **kwargs):
        return "result: %s" % func(*args, **kwargs)
    return _warpper


class T(object):

    def get_name(self):
        return "tony"

    def main(self):
        method = getattr(self, 'get_name')
        print method()
        print "-----------"

    def __getattribute__(self, item):
        v = super(T, self).__getattribute__(item)
        if item == 'get_name':
            return wrapper(v)
        return v

if __name__ == '__main__':
    t = T()
    t.main()