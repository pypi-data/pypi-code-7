# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Base module class.

@author: Arturo Curiel
'''

import zope.interface as zi
import zope.component as zc
from nixtla.core.interfaces import IModule


class BaseModule(object):
    """Every module in the architecture should inherit from this class"""
    zi.implements(IModule)
    
    def __init__(self, marker_interface):
        self.channels = []
        self.marker_interface = marker_interface

        # A marker interface to index the object adapters
        zi.directlyProvides(self, marker_interface)
        IModule.validateInvariants(self)
    
    def __call__(self, input_data):
        """We check input compliance here. System will always call 
           modules as functions.
        """
        self.check_input_compliance(input_data)
        return self.callable(input_data)
    
    def callable(self, input_data):
        """Main functionality of a module is implemented here.
           Called by __call__ after checking input compliance.
        """
        ValueError("Module functionality not implemented")
        
    def add_to_channels(self, adapter_or_module):
        self.channels.append(adapter_or_module)
        IModule.validateInvariants(self)
    
    def send_to_channels(self, message):
        """This method sends a message to every channel"""
        results = []
        for i in range(len(self.channels)):
            results.append(self.channels[i](message))
        return results
    
    def register_module_adapters(self, *adapters):
        """Registers a list of adapters to the global site manager"""
        gsm = zc.getGlobalSiteManager()
        for adapter in adapters:
            gsm.registerAdapter(adapter, 
                                provided=tuple(zi.implementedBy(adapter))[0])
            
    def check_input_compliance(self, input_data):
        """Checks a compliant input for __call__"""
        ValueError("Input checks not implemented!")