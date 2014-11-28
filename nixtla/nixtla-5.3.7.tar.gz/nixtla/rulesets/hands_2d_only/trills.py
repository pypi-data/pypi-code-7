# -*- coding: utf-8 -*-
'''
Created on Nov 16, 2014

@author: Arturo CURIEL
'''
from nixtla.core.tools.model.rules import BaseRule, UndefinedInDomainError
from collections import deque

import math
from nixtla.core.tools.pdlsl import AtomAction


class Trills(BaseRule):
    
    def __init__(self, rule_name, first_art):
        
        if first_art == 'head':
            raise UndefinedInDomainError("Trill not defined for head")
        
        self.first_art = first_art
        super(Trills, self).__init__(AtomAction(rule_name, first_art))
    
    def verify(self, **kwargs):
        
        def distance(point1, point2):
            return math.sqrt((point1[0]-point2[0])**2 + \
                             (point1[1]-point2[1])**2)
            
        movement_points = kwargs['movement_points'] 
        point_list = deque([])
        distance_travelled = 0.
        for point_set in movement_points:
            point = (float(point_set[self.first_art+'_x']),
                     float(point_set[self.first_art+'_y']))
            point_list.append(point)
            if len(point_list) >= 2:
                distance_travelled += distance(point_list[0],
                                               point_list[1])

        if distance_travelled < 5:
            return True
        else:
            return False