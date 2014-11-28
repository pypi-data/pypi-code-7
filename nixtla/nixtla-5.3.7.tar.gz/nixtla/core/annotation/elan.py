# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2014

ELAN annotation class

@author: curiel
'''

from nixtla.core.tools.pympi.Elan import Eaf
from nixtla.core.annotation.markers import IAnnotator

import os

try:
    import magic
except:
    import nixtla.core.tools.magic_win as magic

import zope.interface as zi


class ElanAnnotation(object):
    '''To work only with concurrent per-articulator states/transitions'''
    zi.implements(IAnnotator)
    
    def __init__(self,
                 output_file_path,
                 video_file_path, 
                 input_file_path=None, 
                 author='Nixtla'):
        
        video_file_path = os.path.abspath(video_file_path)        
        self.eaf_file = Eaf(input_file_path, author)
        self.output_file_path = os.path.abspath(output_file_path)
        self.tiers = set(['concurrent',
                          'right_hand',
                          'left_hand'])

        self.eaf_file.add_linked_file(file_path='file://'+video_file_path, 
                                      relpath=video_file_path,
                                      mimetype=magic.from_file(video_file_path, mime=True))
        
        self.eaf_file.add_tier('concurrent',
                               ling='default-lt')
        self.eaf_file.add_tier('right_hand',
                               ling='default-lt')
        #                       parent='concurrent')
        self.eaf_file.add_tier('left_hand',
                               ling='default-lt')
        #                       parent='concurrent')
        
    def create_tiers(self, *tier_names, **kwargs):
        try:
            agents = kwargs['agents']
        except:
            agents = []
            
        for tier in tier_names:
            self.eaf_file.add_tier(tier,
                                   ling='default-lt')
            for agent in agents:
                self.eaf_file.add_tier(tier+"."+agent,
                                       ling='default-lt',
                                       parent=tier)
                self.tiers.add(tier+"."+agent)
            self.tiers.add(tier)
    
    def annotate(self, note, tier, frame_limits):
        if not tier in self.tiers:
            raise KeyError("Not a valid tier")
        
        begin_t = self.frames_to_ms(frame_limits[0])
        end_t = self.frames_to_ms(frame_limits[1] + 1)
        
        try:
            self.eaf_file.insert_annotation(tier, 
                                            begin_t, end_t, 
                                            note)
        except:
            pass
    
    def group_annotate(self, note, tier, group, group_invert=False):
        # Here we will fusion contiguous intervals
        if group_invert:
            group = list(group)
            group.reverse()
            
        current_interval = None
        for member in group:
            if not current_interval:
                # First cycle, we can't determine contiguity
                current_interval = list(member.frame_limits)
            else:
                if current_interval[1] + 1 == member.frame_limits[0]:
                    # They are contiguous, we fusion
                    current_interval[1] = member.frame_limits[1]
                else:
                    # They are not contiguous, we annotate previous
                    # contiguity
                    self.annotate(note, 
                                  tier, 
                                  current_interval)
                    # We restart interval
                    current_interval = list(member.frame_limits)
        if current_interval:
            # We annotate the last found contiguity
            self.annotate(note, 
                          tier, 
                          current_interval)

    def to_keyposture(self, state):
        begin_t = self.frames_to_ms(state.frame_limits[0])
        end_t = self.frames_to_ms(state.frame_limits[1] + 1)
        
        try:
            self.eaf_file.insert_annotation(state.driver,
                                            begin_t, end_t,
                                            'KEYPOSTURE')

        except:
            self.eaf_file.insert_annotation('concurrent',
                                            begin_t, end_t,
                                            'KEYPOSTURE')
            return
        
        level = 0
        for valid_proposition in state.true_values:
            try:
                self.annotate(valid_proposition, 
                              state.driver + "_" + str(level), 
                              state.frame_limits)
            except KeyError, e:
                self.eaf_file.add_tier(state.driver + "_" + str(level),
                                       parent=state.driver)
                self.tiers.add(state.driver + "_" + str(level))
                self.annotate(valid_proposition, 
                              state.driver + "_" + str(level), 
                              state.frame_limits)
            level += 1

    
    def to_movement(self, transition):
        begin_t = self.frames_to_ms(transition.frame_limits[0])
        end_t = self.frames_to_ms(transition.frame_limits[1] + 1)
        try:
            self.eaf_file.insert_annotation(transition.driver, 
                                        begin_t, end_t, 
                                        'MOVEMENT')
        except:
            self.eaf_file.insert_annotation('concurrent', 
                                            begin_t, end_t, 
                                            'MOVEMENT')
            return
                    
        level = 0
        for valid_proposition in transition.true_values:
            try:
                self.annotate(valid_proposition, 
                              transition.driver + "_" + str(level), 
                              transition.frame_limits)
            except KeyError, e:
                self.eaf_file.add_tier(transition.driver + "_" + str(level),
                                       parent=transition.driver)
                self.tiers.add(transition.driver + "_" + str(level))
                self.annotate(valid_proposition, 
                              transition.driver + "_" + str(level), 
                              transition.frame_limits)
            level += 1

    
    def flush(self):
        self.eaf_file.to_file(self.output_file_path)
    
    def frames_to_ms(self, frames, framerate=25):
        return int((1./framerate) * 1000 * frames)
        