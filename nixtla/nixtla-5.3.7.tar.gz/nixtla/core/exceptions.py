# -*- coding: utf-8 -*-
'''
Created on Feb 20, 2014

This module registers exceptions

@author: curiel
'''

import zope.interface as zi


class ImplementationError(zi.Invalid):
    """The object doesn't implement correctly an interface"""
    
    def __repr__(self):
        return "ImplementationError(%r)" % self.args
    

class ConfigError(Exception):
    """Gets called if there is a configuration file error"""