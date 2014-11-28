# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Adapters to handspeed segmentation

@author: Arturo Curiel
'''

import zope.interface as zi
import zope.component as zc

from nixtla.core.interfaces import IModule, IAdapter


class BaseAdapter(object):
    zi.implements(IAdapter)
    
    def __init__(self):
        self.exit_module = None
        IAdapter.validateInvariants(self)
    
    def register_exit_module(self, exit_module):
        if not IModule.providedBy(exit_module):
            raise ValueError("Not a valid channel %s" % str(exit_module))
        self.exit_module = exit_module