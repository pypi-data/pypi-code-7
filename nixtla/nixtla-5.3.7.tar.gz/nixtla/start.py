# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Nixtla (time lapse): Framework for Sign Language Lexical Recognition

@author: curiel
'''

import sys
import os

import zope.component as zc

sys.path.insert(1, os.path.abspath('..'))

from nixtla.core.module_parser import NixtlaModuleParser, INixtlaModuleParser
from nixtla.core.annotation.markers import IAnnotator
from nixtla.core.pipeline import Pipeline

if __name__ == "__main__":
    
    config = NixtlaModuleParser()
    
    # Register the ModuleParser system-wide
    gsm = zc.getGlobalSiteManager()
    gsm.registerUtility(config,
                        INixtlaModuleParser)
    
    config.read("%s/res/config.ini" % sys.path[0])
    
    # Create annotator
    annotator = config.create_annotator()
    gsm.registerUtility(annotator,
                        IAnnotator)
    
    # Create and register declared modules
    modules = config.create_modules()
    
    # Get module providers and module workflow order in Pipeline
    module_order = config.get_module_workflow()
    entry_module = modules[config.get_entry_module()]
    
    # Build pipeline
    pipeline = Pipeline(modules,
                            module_order,
                            entry_module)
    
    pipeline.start()
    annotator.flush()
    sys.exit(0)