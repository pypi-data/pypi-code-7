#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import os

def get_data_file_path(*args):
    """Get path to the specified data file"""
    
    if hasattr(args, '__iter__'):
        if any([not isinstance(a, basestring) for a in args]):
            raise TypeError("argument(s) are not of type string")
        base_path = os.path.realpath(__file__)
        base_dir  = os.path.dirname(base_path)
        file_path = os.path.join(base_dir, *args)
        if not os.path.isfile(file_path):
            raise ValueError("specified data file does not exist")
    else:
        raise TypeError("argument is not of type iterable")
    
    return file_path

def get_data_directory_path():
    """Get path to the data directory"""
    base_path = os.path.realpath(__file__)
    base_dir  = os.path.dirname(base_path)    
    return base_dir
