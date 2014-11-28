# -*- coding: utf-8 -*-
'''
Created on Feb 23, 2014

This module uses ConfigParser as base to parse a config.ini
file

@author: curiel
'''

import ConfigParser
import pyparsing
import zope.interface as zi

from zope.interface.verify import verifyClass, verifyObject

import zope.component as zc

from nixtla.core.exceptions import ConfigError
from nixtla.core.interfaces import IModule
import os


class INixtlaModuleParser(zi.Interface):
    """Marker interface for the module parser"""
    

class NixtlaModuleParser(ConfigParser.SafeConfigParser):
    """Adapts SafeConfigParser to parse module options"""
    zi.implements(INixtlaModuleParser)
    
    def __init__(self):
        ConfigParser.SafeConfigParser.__init__(self)
        self.optionxform = str
        self.module_providers = None
        
    def create_modules(self):
        """Instantiates modules as specified by the config.ini"""
        
        # This method already checks existence of Interface and 
        # their implementations
        providers = self.get_module_providers()
        modules = {}
        for section in providers.keys():
            options = self.options(section)
            
            if "implementedBy" in options:
                options.remove("implementedBy")

            args = {}
            for option in options:
                args[option] = self.get(section, 
                                        option)
            
            if args == {}:
                module = providers[section]['class']()
            else:
                module = providers[section]['class'](**args)
            
            # Verify implementations
            verifyObject(providers[section]['interface'],
                         module)
            verifyObject(IModule, module)
            
            # Register modules as utilities
            gsm = zc.getGlobalSiteManager()
            gsm.registerUtility(module, 
                                providers[section]['interface'])
            
            modules[section] = module
        return modules
        
    def get_class(self, classpath):
        """Dynamically imports class in classpath"""
        imported_module = classpath.split(".")
        class_name = imported_module.pop(-1)
        module_name = str.join(".", imported_module)
        return getattr(__import__(module_name, 
                                  fromlist=[class_name]), 
                       class_name)
    
    def get_entry_module(self):
        """Gets the string indicating the entry module"""
        return self.get("Pipeline", "entry_module")
    
    def output_path(self):
        """Gets the string indicating the resulting eaf path"""
        return self.get("Pipeline", "results_file_path")
    
    def annotation_video_path(self):
        """Gets the string indicating the annotation video path"""
        return self.get("Pipeline", "annotation_video_path")
    
    def create_annotator(self):
        result_path = self.output_path()
        if 'USERPROFILE' in os.environ:
            result_path = result_path.replace("~",
                                              os.environ['USERPROFILE'])
        else:
            result_path = os.path.expanduser(result_path)
        if os.path.exists(result_path):
            os.remove(result_path)
        return self.get_class(self.get("Pipeline", 
                                       "annotator"))(
                                                result_path,
                                                self.annotation_video_path()
                                                )
    
    def get_module_providers(self):
        """Returns a dictionary of the type 
                           {module_name:{'interface' : module_interface,
                                         'class' : module_class},...}
        """
        # Checks if module_providers have already been imported
        if self.module_providers != None:
            return self.module_providers
        
        result = dict(self.items("Modules"))
        for key in result.keys():
            module_interface = self.get_class(result[key])
            if not issubclass(module_interface, zi.Interface):
                raise ConfigError("Invalid interface %s" % \
                                  result[key])
            implementation_path = self.get(key, 'implementedBy')
            module_class = self.get_class(implementation_path)
            
            if verifyClass(module_interface, module_class):
                result[key] = {'interface' : module_interface,
                               'class' : module_class}
            else:
                raise ConfigError("Invalid implementation %s" % \
                                  implementation_path)
        self.module_providers = result
        return self.module_providers
    
    def get_module_workflow(self):
        """Gets the workflow in which the architecture will create the pipeline"""
        
        result = self.get("Pipeline", "workflow")
        result = result.replace("[","(").replace("]",")")
        
        # Parsing parentheses
        comma = pyparsing.Suppress(',')
        content = pyparsing.Word(pyparsing.alphanums) | comma
        parens = pyparsing.nestedExpr('(', ')', content)
        result = parens.parseString(result)
        
        # Converting results to list type
        result = result.asList()
        
        # Reducing dimensions, if possible
        while len(result) == 1:
            result = result[0]
        
        return result
    
    def read(self, filenames):
        # Reads configuration file
        ConfigParser.SafeConfigParser.read(self, filenames)

        # Checks if we have defined any modules
        if not self.has_section('Modules'):
            raise ConfigError("No modules were defined in %s" % filenames)
        
        # Checks if we defined an order for the modules
        if not self.has_section('Pipeline'):
            raise ConfigError("No 'Pipeline' was found in %s" % filenames)
        elif not self.has_option('Pipeline', 'workflow'):
            raise ConfigError("Couldn't parse module workflow in %s" % filenames)
        elif not self.has_option('Pipeline', 'entry_module'):
            raise ConfigError("An entry module needs to be defined in %s"\
                              % filenames)