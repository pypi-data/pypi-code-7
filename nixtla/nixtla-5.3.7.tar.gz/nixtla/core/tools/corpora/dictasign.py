# -*- coding: utf-8 -*-
'''
Created on Nov 16, 2014

Implements a capture designed to process DictaSign corpora video.

@author: Arturo CURIEL
'''

import cv2.cv as cv
import math
import numpy as np

import zope.interface as zi
import zope.component as zc

from nixtla.core.tools.corpora.markers import ICorpusTools
from nixtla.tracking.interface import ITrackingModule


class DictaSignSpecific(object):
    '''This module is intented to hold fine grain methods
    to better analyse image information when creating
    atoms in the modelling module.
    '''
    zi.implements(ICorpusTools)
    
    def __init__(self, video_file_path):
        
        try:
            self.capture = cv.CreateFileCapture(video_file_path)
            if self.capture == None:
                raise IOError("Couldn't open capture file")
            
            self._video_length_in_frames = int(cv.GetCaptureProperty(
                                                self.capture,
                                                cv.CV_CAP_PROP_FRAME_COUNT
                                                ))
            self.video_size = (int(cv.GetCaptureProperty(
                                                self.capture, 
                                                cv.CV_CAP_PROP_FRAME_WIDTH)),
                               int(cv.GetCaptureProperty(
                                                self.capture, 
                                                cv.CV_CAP_PROP_FRAME_HEIGHT))
                               )
            self._fps = 25
        except:
            raise IOError("Couldn't open capture file")

    def hands_touch_visual(self, right_points, left_points, frame):
        '''Returns True if hands touch, False otherwise'''
        image_src = self.seek(frame)
        min_x = int(min(right_points[0],left_points[0]))
        max_x = int(max(right_points[0],left_points[0]))
        
        min_y = int(min(right_points[1],left_points[1]))
        max_y = int(max(right_points[1],left_points[1]))
        
        padding = 25
        
        if min_x - padding > 0 :
            min_x -= padding
        
        #if max_x + padding < self.video_size[0]: 
        if max_x + padding < 720:
            max_x += padding        
        
        if min_y - padding > 0 :
            min_y -= padding
        
        #if max_x + padding < self.video_size[0]: 
        if max_y + padding < 576:
            max_y += padding
        
        # we take a sample of at least 100-pixel height
        roi = image_src[min_y:max_y,
                        min_x:max_x]
        roiHSV = cv.CreateImage(cv.GetSize(roi), 8, 3)
        roiSegmented = cv.CreateImage(cv.GetSize(roi), 8, 1)
        roiDrawContours = cv.CreateImage(cv.GetSize(roi), 8, 3)
        cv.CvtColor(roi, roiHSV, cv.CV_BGR2HSV)
        
        cv.InRangeS(roiHSV, cv.Scalar(0, 10, 60), cv.Scalar(20, 150, 255), roiSegmented)
        
        for i in range(0,6):
            cv.Erode(roiSegmented, roiSegmented)
        for i in range(0,6):
            cv.Dilate(roiSegmented, roiSegmented)
            
        roiContours=cv.CloneImage(roiSegmented)
        storage = cv.CreateMemStorage(0)
        contours = cv.FindContours(roiContours,
                                    storage, 
                                    cv.CV_RETR_TREE,
                                    cv.CV_CHAIN_APPROX_SIMPLE)
        cv.DrawContours(roiDrawContours, 
                        contours, 
                        (0,255,0), 
                        (0,0,255),
                        max_level=2)
        objects = 0
        while contours:
            objects += 1
            contours = contours.h_next()

        cv.ShowImage('1', roi)
        cv.ShowImage('2', roiSegmented)
        cv.ShowImage('3', roiContours)
        cv.ShowImage('4', roiDrawContours)
        cv.WaitKey(0)
        #import ipdb;ipdb.set_trace()

        if objects == 1:
            return True
        else:
            return False
    
    def hands_touch(self, right_points, left_points, frame):
        '''Returns True if hands touch, False otherwise'''
        image_src = self.seek(frame)
        min_x = int(min(right_points[0],left_points[0]))
        max_x = int(max(right_points[0],left_points[0]))
        
        min_y = int(min(right_points[1],left_points[1]))
        max_y = int(max(right_points[1],left_points[1]))
        
        padding = 25
        
        if min_x - padding > 0 :
            min_x -= padding
        
        #if max_x + padding < self.video_size[0]: 
        if max_x + padding < 720:
            max_x += padding        
        
        if min_y - padding > 0 :
            min_y -= padding
        
        #if max_x + padding < self.video_size[0]: 
        if max_y + padding < 576:
            max_y += padding
        
        # we take a sample of at least 100-pixel height
        roi = image_src[min_y:max_y,
                        min_x:max_x]
        roiHSV = cv.CreateImage(cv.GetSize(roi), 8, 3)
        roiSegmented = cv.CreateImage(cv.GetSize(roi), 8, 1)
        roiDrawContours = cv.CreateImage(cv.GetSize(roi), 8, 3)
        cv.CvtColor(roi, roiHSV, cv.CV_BGR2HSV)
        
        cv.InRangeS(roiHSV, cv.Scalar(0, 10, 60), cv.Scalar(20, 150, 255), roiSegmented)
        
        for i in range(0,6):
            cv.Erode(roiSegmented, roiSegmented)
        for i in range(0,6):
            cv.Dilate(roiSegmented, roiSegmented)
            
        roiContours=cv.CloneImage(roiSegmented)
        storage = cv.CreateMemStorage(0)
        contours = cv.FindContours(roiContours,
                                    storage, 
                                    cv.CV_RETR_TREE,
                                    cv.CV_CHAIN_APPROX_SIMPLE)
#         cv.DrawContours(roiDrawContours, 
#                         contours, 
#                         (0,255,0), 
#                         (0,0,255),
#                         max_level=2)
        objects = 0
        while contours:
            objects += 1
            contours = contours.h_next()

#         cv.ShowImage('1', roi)
#         cv.ShowImage('2', roiSegmented)
#         cv.ShowImage('3', roiContours)
#         cv.ShowImage('4', roiDrawContours)
#         import ipdb;ipdb.set_trace()

        if objects == 1:
            return True
        else:
            return False
    
    def seek(self, frame):
        ''''''
        try:
            cv.SetCaptureProperty(self.capture,
                                  cv.CV_CAP_PROP_POS_FRAMES,
                                  frame)
            return cv.QueryFrame(self.capture)
        except Exception as e:
            print "Couldn't change frame position in video capture"
            raise e
    
    def two_vector_angle(self, vector1, vector2, origin=None):
        if origin != None:
            vector1 = (vector1[0]-origin[0],
                       vector1[1]-origin[1])
            vector2 = (vector2[0]-origin[0],
                       vector2[1]-origin[1])
        vector1_magnitude = math.sqrt(vector1[0]**2 + vector1[1]**2)
        vector2_magnitude = math.sqrt(vector2[0]**2 + vector2[1]**2)
        dot_product = vector1[0]*vector2[0] + vector1[1]*vector2[1]
        angle_rad = math.acos(dot_product/(vector1_magnitude*vector2_magnitude))
        return angle_rad*(180./math.pi)
    
    def determinant(self, *points):
        matrix = np.zeros(shape=(len(points),len(points)))
        for i in range(0, len(points)):
            matrix[i] = tuple(1 for _ in range(0, len(points)-2)) + points[i]
        result = np.linalg.det(matrix)
        return result

    def rotation_orientation(self, det_result):
        if det_result < 0:
            return 'neg'
        else:
            return 'pos'
            
    def clockwise_orientation(self, v1, v2):
        return self.orientation(v1, v2) >= 0
    
    def counterclockwise_orientation(self, v1, v2):
        return self.orientation(v1, v2) < 0
    
    def orientation(self, v1, v2):
        return (float(v1[0])*float(v2[1]))-(float(v2[0])*float(v1[1]))
    
    def is_convex_set(self, point_list):
        ''''''
        old_orientation = None
        if len(point_list) > 3:
            point_list.append(point_list[0])
            point1 = point_list[0]
            point2 = point_list[1]
            vector1 = (point2[0]-point1[0],
                       point2[1]-point1[1])
            for point in point_list[2:]:
                point1 = point2
                point2 = point
                vector2 = (point2[0]-point1[0],
                           point2[1]-point1[1])
                new_orientation = self.orientation(vector1, vector2) < 0
                if old_orientation == None:
                    old_orientation = new_orientation
                else:
                    if old_orientation != new_orientation:
                        return False
                vector1 = vector2
            point_list.pop()
        else:
            return False
        return True
    
    def is_convex_set_det(self, point_list):
        ''''''
        old_orientation = None
        max_det = None
        if len(point_list) > 3:
            point1 = point_list[0]
            point2 = point_list[1]
            for point3 in point_list[2:]:
                det_result = self.determinant(point1, point2, point3)
                max_det = max(max_det, det_result)
                new_orientation = self.rotation_orientation(det_result)
                old_orientation = old_orientation or new_orientation
                if old_orientation != new_orientation:
                    return None
                point1 = point2
                point2 = point3
        else:
            return None
        return max_det
    
    def play(self, limits, sign_name="sign_name",
             paint_points=False):
        end_segment = False
        return_value = False
        cv.NamedWindow(sign_name, cv.CV_WINDOW_AUTOSIZE)
        cv.StartWindowThread()
        while not end_segment:
            self.seek(limits[0])
            for frame_number in range(*limits) + [limits[1]]:
                frame = self.query()
                if paint_points:
                    frame = self.paint_points(frame, frame_number)
                cv.ShowImage(sign_name, frame)
                cv.WaitKey(50)
            keycode = cv.WaitKey()
            if keycode == 1048603:
                # ESC
                end_segment = True
            elif keycode == 1048675:
                # C
                # Confirms sign
                return_value = True
                end_segment = True
        cv.DestroyWindow(sign_name)
        cv.WaitKey(1)
        return return_value
    
    def paint_points(self, img, frame_number):
        frame_tracking_data = zc.getUtility(ITrackingModule).tracker.\
                            tracking_data[frame_number]
        point_list = []
        color_roulette = [(255, 0, 0),
                          (0, 255, 0),
                          (0, 0, 255)]
        
        for key in frame_tracking_data.keys():
            if key != 'frame':
                point_list.append(map(int, np.round(frame_tracking_data[key])))

        for color, point in enumerate(point_list):
            #import ipdb;ipdb.set_trace()
            cv.Circle(img, 
                      tuple(point), 
                      3, 
                      color_roulette[color % len(color_roulette)])
        return img
    
    def query(self):
        return cv.QueryFrame(self.capture)