#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from pyselection.core import const_types
import sys

# Constant module solution taken from: 
# Martelli and Asher (2002) Python Cookbook. Sebastopol: O'Reilly. (p.193)

class _const(object):
    """Class for storing constant values."""
    
    def __init__(self):
        self.const_types = const_types
    
    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise TypeError("cannot rebind const (%s)" % key)
        if hasattr(self, "const_types") and not isinstance(value, self.const_types):
            raise TypeError("cannot bind value of type %s to const (%s)" % 
              (type(value).__name__, key) )
        self.__dict__[key] = value

    def __delattr__(self, key):
        if key in self.__dict__:
            raise TypeError("cannot unbind const (%s)" % key)
        raise NameError(key)

sys.modules[__name__] = _const()
