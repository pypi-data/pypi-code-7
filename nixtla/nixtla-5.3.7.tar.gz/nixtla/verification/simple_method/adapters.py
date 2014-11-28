# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Adapters to handspeed segmentation

@author: Arturo Curiel
'''

import zope.interface as zi
import zope.component as zc

import pandas as pd
import numpy as np

from nixtla.verification.simple_method.markers import ISimpleVerification
from nixtla.modelling.channel_based.markers import IChannelBasedModel

from nixtla.core.base_adapter import BaseAdapter
from nixtla.core.annotation.markers import IAnnotator


class FromChannelModel(BaseAdapter):
    # Adapts hands/head text tracking input to a segmentable object
    zi.implements(ISimpleVerification)
    zc.adapts(IChannelBasedModel)
    
    def __init__(self, context):
        self.modelling_module = context
        self.annotator = zc.getUtility(IAnnotator)
        super(FromChannelModel, self).__init__()
    
    def __call__(self, input_data):
        """We are receiving the output of an IChannelBasedModel call:
           
            we are adapting to a ISimpleVerification input.
        """
        if self.exit_module.db == None:
            self.exit_module.read_database(self.modelling_module.ruleset,
                                           self.modelling_module.articulators)
        history = input_data
        if len(history) >= (self.modelling_module.history_verification_length / 3.) * 3.:
        #if len(history) >= 40 :
            #history.dump()
            state = history.popfirststate()
        else:
            state = None
        return self.exit_module(state)