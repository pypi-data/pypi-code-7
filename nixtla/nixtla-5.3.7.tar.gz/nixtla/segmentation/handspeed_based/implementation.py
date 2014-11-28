# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Implementation of a hand speed-based segmentation module

@author: Arturo Curiel
'''

import zope.interface as zi

try:
    import magic
except:
    import nixtla.core.tools.magic_win as magic

from nixtla.core.base_module import BaseModule
from nixtla.segmentation.interface import ISegmentationModule

from nixtla.segmentation.handspeed_based.adapters import FromTextTracking
from nixtla.segmentation.handspeed_based.markers import IHandSpeedBasedSegments

from nixtla.segmentation.handspeed_based.tools import IntervalList


class SegmentationModule(BaseModule):
    """Hand speed-based segmentation"""
    zi.implements(ISegmentationModule)
    
    def __init__(self, **args):
        
        try:
            self.analysis_window = int(args['analysis_window'])
        except:
            self.analysis_window = 5
        
        try:
            self.speed_threshold = int(args['speed_threshold'])
        except:
            self.speed_threshold = 6.0
            
        try:
            self.articulators = args['articulators'].\
                                replace('[','').\
                                replace(']','').\
                                replace(' ','').\
                                split(",")
        except:
            self.articulators = ['right_hand', 'left_hand']
        
        self.numeric_data = None
        # Register adapters
        self.register_module_adapters(FromTextTracking)
        
        self.interval_list = IntervalList(self.speed_threshold,
                                          articulators=self.articulators,
                                          driver=self.articulators[0])
        
        super(SegmentationModule, self).__init__(IHandSpeedBasedSegments)
    
    def callable(self, input_data):
        signer_id, numeric_data = input_data
        self.numeric_data = numeric_data
        for i in range(len(numeric_data)-1):
            row = numeric_data[i:i+1]
            
            # We get each information row and pass it to determine where in
            # the segmentation it belongs
            for articulator in self.articulators:
                results = self.interval_list.\
                                include_in_articulator_interval_2window(
                                                                articulator,
                                                                row)
                if results:
                    for result in results:
                        self.send_to_channels((signer_id,
                                               {articulator:result}
                                             ))
        return True

    def check_input_compliance(self, input_data):
        """Assert that input_data is segmentable"""
        # Check that we are still passing a valid
        # video file and an id
        assert len(input_data) == 2
        assert "str" in str(type(input_data[0]))
        
        # Check that we are passing speeds, the only
        # measure truly needed to calculate segments
        for articulator in self.articulators:
            assert not input_data[1][articulator+'_v'].empty