# -*- coding: utf-8 -*-
'''
Created on Feb 20, 2014

Tools to create an architecture from system modules

@author: curiel
'''

import zope.interface as zi
import zope.component as zc

from nixtla.core.interfaces import IPipeline


class Pipeline(object):
    """Implements the main architecture context"""
    zi.implements(IPipeline)
    
    def __init__(self, registered_modules, module_order, entry_module):
        self.registered_modules = registered_modules
        self.module_order = module_order
        self.entry_module = entry_module
        
        self.build_pipeline()
        IPipeline.validateInvariants(self)
    
    def start(self, *args):
        """Start processing"""
        return self.entry_module(args)
    
    def build_pipeline(self):
        """This method adapts every module to each other and establishes
        who will communicate with who"""
        
        for binary_rel in self.module_order:
            input_mod = self.registered_modules[binary_rel[0]]
            output_mod = self.registered_modules[binary_rel[1]]
            
            input_mod.add_to_channels(self.adapt_to(input_mod, output_mod))
            
    def adapt_to(self, origin, destination):
        """This method searches for an adapter from origin to destination."""
        
        try:
            destination_interface = tuple(zi.directlyProvidedBy(destination))[0]
            adapter = zc.getAdapter(origin, destination_interface)
            adapter.register_exit_module(destination)
            return adapter
        except:
            return destination