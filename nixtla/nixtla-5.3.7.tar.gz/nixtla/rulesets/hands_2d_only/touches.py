# -*- coding: utf-8 -*-
'''
Created on Nov 16, 2014

Touching between two articulators

@author: Arturo CURIEL
'''

from nixtla.core.tools.model.rules import BaseRule, UndefinedInDomainError
from nixtla.core.tools.corpora.markers import ICorpusTools
from nixtla.core.tools.pdlsl import Atom

import zope.component as zc

import math


class Touches(BaseRule):
    
    def __init__(self, rule_name, first_art, second_art):
        try:
            self.corpus_specific = zc.getUtility(ICorpusTools)
        except:
            self.corpus_specific = None
        
        if first_art == second_art:
            raise UndefinedInDomainError("An articulator can't touch itself: %s" % first_art)
        
        self.first_art = first_art
        self.second_art = second_art
        self.touching_threshold = 65.0
        super(Touches, self).__init__(Atom(rule_name, first_art))
        
    def verify(self, **kwargs):
        config = kwargs['average_data']
        point1 = config[self.first_art]
        point2 = config[self.second_art]
        frame = int(config['frame'])
        
        distance = math.sqrt((point1[1] - point2[1])**2 + (point1[0] - point2[0])**2)
        if distance < self.touching_threshold:
            if self.corpus_specific == None :
                return True
            else:
                #import ipdb;ipdb.set_trace()
                return self.corpus_specific.hands_touch(point1,
                                                        point2,
                                                        frame)
        return False