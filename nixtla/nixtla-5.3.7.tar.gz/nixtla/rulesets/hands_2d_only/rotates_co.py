# -*- coding: utf-8 -*-
'''
Created on Nov 16, 2014

@author: Arturo CURIEL
'''
from nixtla.core.tools.model.rules import BaseRule, UndefinedInDomainError

from collections import deque

import math
from nixtla.core.tools.pdlsl import AtomAction


class RotatesCounterclockwise(BaseRule):
    
    def __init__(self, rule_name, first_art):

        if first_art == 'head':
            raise UndefinedInDomainError("Head can't rotate")

        self.first_art = first_art
        super(RotatesCounterclockwise, self).__init__(AtomAction(rule_name, first_art))
    
    def verify(self, **kwargs):
        
        movement_points = kwargs['movement_points']
        point_list = deque([])
        result = None
        result_list = []
        
        # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
        # Returns a positive value, if OAB makes a counter-clockwise turn,
        # negative for clockwise turn, and zero if the points are collinear.
        def cross_product(origin, p1, p2):
            return (p1[0] - origin[0]) * (p2[1] - origin[1]) - \
                (p1[1] - origin[1]) * (p2[0] - origin[0])
        
        for point_set in movement_points:
            point = (float(point_set[self.first_art+'_x']),
                     float(point_set[self.first_art+'_y']))
            point_list.append(point)
            #if len(point_list) >= 3:
            if len(point_list) > 6:
                cp = cross_product(point_list[0], point_list[1], point_list[2])
                if cp >= 0:
                    # counter-clockwise turn or collinear
                    if not result:
                        result = [point_list[0],
                                  point_list[1],
                                  point_list[2]
                                  ]
                    else:
                        result.append(point_list[2])
                else:
                    # clockwise turn
                    if result:
                        result_list.append(result)
                        result = None

        if result:
            result_list.append(result)
        # We might have found multiple instances, just get the longest
        longest_result = None
        for found_result in result_list:
            if not longest_result:
                longest_result = found_result
            else:
                if found_result > len(longest_result):
                    longest_result = found_result

        # If the longest convex hull has more than 
        # half of the points, accept it
        if not longest_result:
            return False
        elif len(longest_result) > .5*len(movement_points):
            return True
        return False
