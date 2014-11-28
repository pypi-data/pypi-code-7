# -*- coding: utf-8 -*-
'''
Created on Nov 16, 2014

@author: Arturo CURIEL
'''
from nixtla.core.tools.model.rules import BaseRule, UndefinedInDomainError

from collections import deque

import math
from nixtla.core.tools.pdlsl import AtomAction


class Rotates(BaseRule):
    
    def __init__(self, rule_name, first_art):

        if first_art == 'head':
            raise UndefinedInDomainError("Head can't rotate")
        
        self.first_art = first_art
        super(Rotates, self).__init__(AtomAction(rule_name, first_art))
    
    def verify(self, **kwargs):
        
        def distance(point1, point2):
            return math.sqrt((point1[0]-point2[0])**2 + \
                             (point1[1]-point2[1])**2)
            
        def angle(point1, origin, point2):
            do1 = distance(origin, point1)
            do2 = distance(origin, point2)
            d12 = distance(point1, point2)
            try:
                return math.acos((do1 ** 2 + do2 ** 2 - d12 ** 2) / (2 * do1 * do2))
            except:
                return 0
        
        movement_points = kwargs['movement_points']
        first_point = None
        point_list = deque([])
        current_result = 0.
        distance_travelled = 0.
        result_list = []
        for point_set in movement_points:
            point = (float(point_set[self.first_art+'_x']),
                     float(point_set[self.first_art+'_y']))
            if not first_point:
                first_point = point
            point_list.append(point)
            if len(point_list) >= 2:
                distance_travelled += distance(point_list[0], 
                                               point_list[1])
            if len(point_list) >= 3:
                angle_value = angle(point_list[0],
                                    point_list[1],
                                    point_list[2])
                if angle_value < math.pi:
                    # Convex
                    current_result += angle_value
                    if current_result >= math.pi:
                        dfo = distance(first_point, point_list[1])
                        if dfo < 30:
                            return False
                else:
                    return False
                    result_list.append(current_result)
                    current_result = 0.
                point_list.popleft()
        
        if current_result > 0.:
            result_list.append(current_result)

        try:
            if max(result_list) > math.pi:
                return True
        except:
            pass
        
        return False