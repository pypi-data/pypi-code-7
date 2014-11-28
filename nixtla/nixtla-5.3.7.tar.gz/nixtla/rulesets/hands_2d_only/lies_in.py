# -*- coding: utf-8 -*-
'''
Created on Nov 16, 2014

Articulator located in some place with respect to another articulor

@author: Arturo CURIEL
'''

from nixtla.core.tools.model.rules import BaseRule, UndefinedInDomainError

import math
from nixtla.core.tools.pdlsl import Atom


class LiesIn(BaseRule):
    
    def __init__(self, rule_name, first_art, second_art, direction):
        
        if first_art == second_art:
            raise UndefinedInDomainError("An articulator can't touch itself: %s" % first_art)
        
        self.first_art = first_art
        self.second_art = second_art
        self.direction = direction
        super(LiesIn, self).__init__(Atom(rule_name, first_art))
    
    def verify(self, **kwargs):
       
        def angle(point1, point2):
            '''Returns angle of the line formed by two points, with respect
            to x-axis'''
            try:
                m = (point2[1] - point1[1]) / (point2[0] - point1[0])
            except:
                # No slope, vertical movement
                if point1[1] < point2[1]:
                    return 3 * math.pi / 2
                else:
                    return math.pi / 2
            #angle_value = math.atan2(m, 1)
            y = ((-point2[1]) - (-point1[1])) # orig in upper-left corner of img
            x = (point2[0] - point1[0])
            angle_value = math.atan2(y, x)
            if angle_value < 0:
                angle_value += 2 * math.pi
            return angle_value
        
        tracking_data = kwargs['average_data']
        point1 = tracking_data[self.first_art]
        point2 = tracking_data[self.second_art]
        
        angle_value = angle(point2, point1)
        if 0 <= angle_value < math.pi / 6 or\
           11 * math.pi / 6 <= angle_value < 2 * math.pi:
            looked_up_direction = "RIGHT"
        elif math.pi / 6 <= angle_value < math.pi / 3:
            looked_up_direction = "UP_RIGHT"
        elif math.pi / 3 <= angle_value < 2 * math.pi / 3:
            looked_up_direction = "UP"
        elif 2 * math.pi / 3 <= angle_value < 5 * math.pi / 6:
            looked_up_direction = "UP_LEFT"
        elif 5 * math.pi / 6 <= angle_value < 7 * math.pi / 6:
            looked_up_direction = "LEFT"
        elif 7 * math.pi / 6 <= angle_value < 4 * math.pi / 3:
            looked_up_direction = "DOWN_LEFT"
        elif 4 * math.pi / 3 <= angle_value < 5 * math.pi / 3:
            looked_up_direction = "DOWN"
        elif 5 * math.pi / 3 <= angle_value < 11 * math.pi / 6:
            looked_up_direction = "DOWN_RIGHT"

        if self.direction == looked_up_direction:
            return True
        return False
