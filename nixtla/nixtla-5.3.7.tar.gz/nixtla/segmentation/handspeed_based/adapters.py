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

from nixtla.tracking.text_based.markers import ITextBasedTracker
from nixtla.segmentation.handspeed_based.markers import IHandSpeedBasedSegments

from nixtla.core.base_adapter import BaseAdapter


class FromTextTracking(BaseAdapter):
    # Adapts hands/head text tracking input to a segmentable object
    zi.implements(IHandSpeedBasedSegments)
    zc.adapts(ITextBasedTracker)
    
    def __init__(self, context):
        self.tracking_module = context
        super(FromTextTracking, self).__init__()
    
    def angle_in_deg(self, origin_x, origin_y, point_x, point_y):
        '''
        Calculates angle from (origin_x, origin_y) to (point_x, point_y)
        
                                90°
         
                       |180°| origin 0°

                               -90°
        '''
        
        # The angle of (point_x, point_y) w.r.t a line parallel 
        # to X passing through (origin_x, origin_y).
        ca = point_x-origin_x
        
        #Inverted Y
        co = origin_y-point_y
        h = np.sqrt(ca**2 + co**2)
        
        rad_angle = np.arctan2(co, ca)
        deg_angle = rad_angle*(180./np.pi)
        return deg_angle
    
    def __call__(self, input_data):
        """We are receiving the output of an ITextBasedTracker call:
           
           input_data = ('SignerX',
                         '/path/to/video',
                         pd.DataFrame({art1:np.array([...]), art2:...}))
                         
            we are adapting to a IHandSpeedBasedSegment input:
            
            
        """
        raw_data = input_data[1]
        mean_data = pd.rolling_mean(raw_data, 
                                window=self.exit_module.analysis_window
                                ).shift(-2)
        
        #Speed and acceleration
        first_diff = mean_data.diff(2).shift(-1)
        first_diff = first_diff / 2. # speed in pix/frame
        second_diff = first_diff.diff(2).shift(-1)
        second_diff = second_diff / 2. # accel in pix/frame^2
        
        norm_op = lambda x, y:np.sqrt(x**2 + y**2)
        
        raw_data['head_v'] = norm_op(first_diff.head_x,
                                     first_diff.head_y)
        raw_data['left_hand_v'] = norm_op(first_diff.left_hand_x,
                                     first_diff.left_hand_y)
        raw_data['right_hand_v'] = norm_op(first_diff.right_hand_x,
                                      first_diff.right_hand_y)
        
        raw_data['head_a'] = norm_op(second_diff.head_x,
                                     second_diff.head_y)
        raw_data['left_hand_a'] = norm_op(second_diff.left_hand_x,
                                     second_diff.left_hand_y)
        raw_data['right_hand_a'] = norm_op(second_diff.right_hand_x,
                                      second_diff.right_hand_y)
        
        raw_data['ang_left_right'] = self.angle_in_deg(raw_data.left_hand_x, 
                                                       raw_data.left_hand_y, 
                                                       raw_data.right_hand_x, 
                                                       raw_data.right_hand_y)
        
        raw_data['ang_right_left'] = self.angle_in_deg(raw_data.right_hand_x, 
                                                       raw_data.right_hand_y, 
                                                       raw_data.left_hand_x, 
                                                       raw_data.left_hand_y)
        raw_data['frame'] = range(len(raw_data))
        raw_data = raw_data.fillna(0.)
        return self.exit_module((input_data[0], raw_data))