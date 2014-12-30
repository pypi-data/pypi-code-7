# -*- coding: utf-8 -*-

import json

class Payload(object):
    def __init__(self, str_or_dict):
        
        if type(str_or_dict) == type({}):
            self.__dict__ = str_or_dict
        else:
            self.__dict__ = json.loads(str_or_dict)

        #recursive convert dict to python object
        for k in self.__dict__:
            if type(self.__dict__[k]) == type({}):
                self.__dict__[k] = Payload(self.__dict__[k])


def loads(s):
    return Payload(s)

if __name__ == '__main__':
    print "qjson", __version__