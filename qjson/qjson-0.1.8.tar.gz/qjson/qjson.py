# -*- coding: utf-8 -*-

import json

class Payload(object):
    def __init__(self, str_or_dict):
        
        if isinstance(str_or_dict, dict):
            self.__dict__ = str_or_dict
        else:
            dict_or_list = json.loads(str_or_dict)

            if isinstance(dict_or_list, dict):
                self.__dict__ = dict_or_list

            if isinstance(dict_or_list, list):
                self.__item__ = dict_or_list

        #recursive convert dict to python object
        for k in self.__dict__:
            if isinstance(self.__dict__[k], dict):
                self.__dict__[k] = Payload(self.__dict__[k])

            if isinstance(self.__dict__[k], list):
                for idx, val in enumerate(self.__dict__[k]):
                    if isinstance(val, dict):
                        self.__dict__[k][idx] = Payload(self.__dict__[k][idx])
    
    def __getitem__(self, key):
        return self.__item__[key]

def loads(s):
    return Payload(s)

if __name__ == '__main__':
    print "qjson - quick and dirty way to convert json string to python object"