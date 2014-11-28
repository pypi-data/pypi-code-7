# -*- coding: utf-8 -*-
'''
Created on Nov 16, 2014

@author: Arturo CURIEL
'''

from nixtla.core.tools.model.rules import BaseRule, UndefinedInDomainError

import math
from nixtla.core.tools.pdlsl import AtomAction


class MovesTo(BaseRule):
    
    def __init__(self, rule_name, first_art, direction):
        
        self.first_art = first_art
        self.direction = direction
        super(MovesTo, self).__init__(AtomAction(rule_name, first_art))
    
    def verify(self, **kwargs):

        origin_raw_data = kwargs['starting_point_tracking']
        ending_raw_data = kwargs['end_point_tracking']
        
        # We are receiving two rows of a pandas data frame
        point1 = (float(origin_raw_data[self.first_art + "_x"]),
                  float(origin_raw_data[self.first_art + "_y"]))
        point2 = (float(ending_raw_data[self.first_art + "_x"]),
                  float(ending_raw_data[self.first_art + "_y"]))
        
        #distance = math.sqrt((point1[1] - point2[1])**2 + (point1[0] - point2[0])**2)
        #articulator_moved = distance > kwargs['touching_distance']
        
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
            # angle_value = math.atan2(m, 1)
            y = ((-point2[1]) - (-point1[1])) # orig in upper-left corner of img
            x = (point2[0] - point1[0])
            angle_value = math.atan2(y, x)
            if angle_value < 0:
                angle_value += 2 * math.pi
            return angle_value
        
        #if articulator_moved:
        angle_value = angle(point1, point2)
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
