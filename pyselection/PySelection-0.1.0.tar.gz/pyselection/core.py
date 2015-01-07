#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import sys
from types import NoneType

class _core(object):
    """Class for package settings."""
    
    def is_sized_iterable(self, x):
        return hasattr(x, "__iter__") and hasattr(x, "__len__")
    
    def __init__(self):
        
        if sys.version_info[0] == 3 and sys.version_info[1] >= 1:

            self.int_types = (int,)
            self.str_types = (str,)
            
            self.range = range
            
        elif sys.version_info[0] == 2 and sys.version_info[1] >= 6:
           
            self.int_types = (int, long)
            self.str_types = (basestring, unicode)
            
            self.range = xrange
        
        else:
            raise RuntimeError("Python version 2.6+ or 3.1+ is required")
        
        self.table_data_types = (int, float, long, complex, bool, basestring, unicode, NoneType)
        self.const_types = (int, float, long, complex, bool, basestring, unicode, frozenset)
        
        self.locked = True

    def __setattr__(self, key, value):
        if hasattr(self, "locked") or key in self.__dict__:
            raise TypeError("cannot rebind package settings")
        self.__dict__[key] = value

    def __delattr__(self, key):
        raise TypeError("cannot unbind package settings")

# Solution adapted from constant module code in: 
# Martelli and Asher (2002) Python Cookbook. Sebastopol: O'Reilly. (p.193)
################################################################################ 

sys.modules[__name__] = _core()

################################################################################