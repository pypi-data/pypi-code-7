# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Implementation of a text based hands and head tracking module

@author: Arturo Curiel
'''

import zope.interface as zi
import zope.component as zc

import pandas as pd
import numpy as np
try:
    import magic
except:
    import nixtla.core.tools.magic_win as magic
import os

from nixtla.core.base_module import BaseModule
from nixtla.tracking.interface import ITrackingModule

from nixtla.tracking.text_based.markers import ITextBasedTracker
from nixtla.core.tools.corpora.markers import ICorpusTools
from nixtla.core.module_parser import INixtlaModuleParser


class TrackingModule(BaseModule):
    """Text based hands and head tracking module"""
    zi.implements(ITrackingModule)
    
    def __init__(self, **args):
        try:
            self.rounded = args['rounded']
            assert isinstance(self.rounded, bool)
        except:
            self.rounded = False
        
        try:
            tracking_files = args['tracking_files']
            tracking_files = tracking_files.replace("[", "").\
                                            replace("]","").\
                                            replace(" ", "")
            self.tracking_files = tracking_files.split(",")
        except KeyError:
            raise KeyError("No tracking file specified.")
        
        try:
            raw_video_file = args['raw_video_file']
            if not 'video/' in magic.from_file(raw_video_file, mime=True):
                raise ValueError("Not a valid video file: %s", raw_video_file)
            config = zc.getUtility(INixtlaModuleParser)
            corpus_toolbox_class = config.get_class(
                                                args['corpus_processing_class']
                                                )
            corpus_toolbox = corpus_toolbox_class(raw_video_file)
            # Register corpus tools system-wide
            gsm = zc.getGlobalSiteManager()
            gsm.registerUtility(corpus_toolbox,
                                ICorpusTools)
        except Exception, e:
            raise ValueError("Couldn't register corpus toolbox")
        
        if len(self.tracking_files) > 2:
            raise ValueError("We can process at most two signers per video")
        
        # Mark this module with a unique interface
        super(TrackingModule, self).__init__(ITextBasedTracker)

    def callable(self, input_data):
        i=0;
        results = []
        for tracking_file in self.tracking_files:
            # Check if this file exists
            if not os.path.exists(tracking_file):
                raise ValueError("File not found: %s" % tracking_file)
            
            # It exists, parse it and send it
            results.append(self.send_to_channels(('Signer'+str(i),
                                   self.parse_tracking(tracking_file,
                                                       self.rounded)
                                   )
                                  )
                           )
            i+=1
        return results
    
    def parse_tracking(self, tracking_file, rounded=False):
        """Parses the given tracking file"""
        try:
            t_file = open(tracking_file,"r")
            tracking_data = t_file.readlines()
            t_file.close()
        except Exception, e:
            raise ValueError("Couldn't read tracking file %s" % tracking_file)
        
        numeric_data = {'head_x': np.zeros(len(tracking_data)),
                        'head_y': np.zeros(len(tracking_data)),
                        'right_hand_x' : np.zeros(len(tracking_data)),
                        'right_hand_y' : np.zeros(len(tracking_data)),
                        'left_hand_x' : np.zeros(len(tracking_data)),
                        'left_hand_y' : np.zeros(len(tracking_data))
                        }
        
        for tracking_line in tracking_data:
            broken_line = tracking_line.replace("\n","").split("\t")

            if len(broken_line) != 7:
                break
            
            i = int(broken_line[0])
            if rounded:
                numeric_data['head_x'][i] = round(float(broken_line[1]))
                numeric_data['head_y'][i] = round(float(broken_line[2]))
                numeric_data['right_hand_x'][i] = round(float(broken_line[3]))
                numeric_data['right_hand_y'][i] = round(float(broken_line[4]))
                numeric_data['left_hand_x'][i] = round(float(broken_line[5]))
                numeric_data['left_hand_y'][i] = round(float(broken_line[6]))
            else:
                numeric_data['head_x'][i] = float(broken_line[1])
                numeric_data['head_y'][i] = float(broken_line[2])
                numeric_data['right_hand_x'][i] = float(broken_line[3])
                numeric_data['right_hand_y'][i] = float(broken_line[4])
                numeric_data['left_hand_x'][i] = float(broken_line[5])
                numeric_data['left_hand_y'][i] = float(broken_line[6])
                
        #numeric_data['frame'] = range(len(tracking_data))
        #return numeric_data
        return pd.DataFrame(numeric_data)
    
    def check_input_compliance(self, input_data):
        """Assert that input_data points to a real video file"""
        
        # This implementation doesn't really need anything to start
        assert len(input_data) == 0