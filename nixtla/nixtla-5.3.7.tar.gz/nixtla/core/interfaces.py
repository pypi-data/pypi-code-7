# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Core components interfaces

@author: Arturo Curiel
'''

import zope.interface as zi

from nixtla.core.exceptions import ImplementationError


def check_module(obj):
    """Check if the Module object implements a list of Modules
    """
    try:
        if isinstance(obj.channels, list):
            for channel in obj.channels:
                if not IModule.providedBy(channel) and\
                   not IAdapter.providedBy(channel):
                    raise ImplementationError(obj)
        else:
            raise ImplementationError(obj)
    except:
        raise ImplementationError(obj)
    

class IModule(zi.Interface):
    """A system module with a MRSW buffer"""
    
    channels = zi.Attribute("""A list of modules, representing output 
                               communication channels""")
    
    def __call__(input_data):
        """We check input compliance here. System will always call 
           modules as functions.
        """
    
    def callable(input_data):
        """Main functionality of a module is implemented here.
           Called by __call__ after checking input compliance.
        """
        
    def add_to_channels(adapter_or_module):
        """Adds a new channel and checks if object is still
        compliant.
        """
        
    def send_to_channels(message):
        """This method sends a message to every
        channel"""
        
    def register_module_adapters(*adapters):
        """Registers a list of adapters to the global site manager"""
        
    def check_input_compliance(input_data):
        """Checks a compliant input for __call__"""

    zi.invariant(check_module)


def check_adapter(obj):
    try:
        if obj.exit_module:
            assert IModule.providedBy(obj)
    except:
        raise ImplementationError(obj)


class IAdapter(zi.Interface):
    
    exit_module = zi.Attribute("The module to which we want to adapt")
    
    def register_exit_module(exit_module):
        """Registers an exit module"""
        
    zi.invariant(check_adapter)
    
def valid_order(lst_order, uid_list):
    """Checks if lst_order is compatible with IArchitecture"""
    try:
        for element in lst_order:
            if isinstance(element, list):
                if not valid_order(element, 
                                   uid_list):
                    return False
            else:
                if not element in uid_list:
                    return False
    except:
        return False
    return True


def check_architecture(obj):
    """Check that the architecture provides the correct type of data"""
    try:
        for key in obj.registered_modules.keys():
            if not IModule.providedBy(obj.registered_modules[key]):
                raise ImplementationError(obj)
        
        if not valid_order(obj.module_order, 
                           obj.registered_modules.keys()):
            raise ImplementationError(obj)
        
        if not IModule.providedBy(obj.entry_module):
            raise ImplementationError(obj)
        
    except Exception, e:
        raise ImplementationError(obj)


class IPipeline(zi.Interface):
    """Describes the architecture of a system formed with a list 
       of IModule implementations
    """
    registered_modules = zi.Attribute("""Dict of registered mods in the 
                                         architecture""")
    module_order = zi.Attribute("""Lists the order in which modules are 
                                   processed""")
    entry_module = zi.Attribute("""Holds the first module in the pipeline, to be called
                                   at the beginning of each loop""")
    
    def start(*args):
        """Method to start processing"""

    zi.invariant(check_architecture)