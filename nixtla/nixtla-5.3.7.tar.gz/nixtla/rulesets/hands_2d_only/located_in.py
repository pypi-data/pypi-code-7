# -*- coding: utf-8 -*-
'''
Created on Nov 16, 2014

Articulator located in some place of articulation

@author: Arturo CURIEL
'''

import sys

from nixtla.core.tools.model.rules import BaseRule, UndefinedInDomainError

from nixtla.core.tools.pdlsl import Atom

from nixtla.core.tools.spacedata import RegionTree


class LocatedIn(BaseRule):
    
    def __init__(self, rule_name, first_art, region_name):
        
        if first_art == 'head':
            raise UndefinedInDomainError("Head will always be on the same region")
        
        self.first_art = first_art
        self.region_name = region_name
        
        self.region_tree, self.region_stack = RegionTree.tree_from_xml(
                                        "%s/res/simple_revised_regionsA.xml" %\
                                         sys.path[0]
                                        )
        super(LocatedIn, self).__init__(Atom(rule_name, first_art))
    
    def verify(self, **kwargs):
        config = kwargs['average_data']
        region_tree = self.region_tree
        loc_point = config[self.first_art]
        calculated_regions = region_tree.search_point(loc_point)
        if self.region_name in calculated_regions:
            return True
        return False