# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Implementation of a channel based modelling module

@author: Arturo Curiel
'''

import zope.interface as zi
import zope.component as zc

from nixtla.core.base_module import BaseModule
from nixtla.core.tools.model.rules import BaseRuleSet
#from nixtla.rulesets.hands_2d_only.ruleset import Hands2DRuleset
from nixtla.modelling.interface import IModellingModule
from nixtla.modelling.channel_based.markers import IChannelBasedModel

from nixtla.core.tools.model.concurrent_history import ArticulatorState
from nixtla.core.tools.model.concurrent_history import ArticulatorTransition
from nixtla.core.tools.model.concurrent_history import ConcurrentHistory

import numpy as np
from nixtla.segmentation.interface import ISegmentationModule
from nixtla.segmentation.handspeed_based.tools import Interval

class ModellingModule(BaseModule):
    """Channel based modelling module"""
    zi.implements(IModellingModule)
    
    def __init__(self, **args):
        
        # load ruleset
        self.ruleset = BaseRuleSet(args["ruleset"])
        try:
            self.articulators = args['articulators'].replace('[','').\
                                                     replace(']','').\
                                                     replace(' ','').\
                                                     split(',')
        except:
            self.articulators = ['right_hand', 'left_hand']
            
        try:
            self.history_verification_length = int(
                                            args['history_verification_length']
                                            )
        except:
            self.history_verification_length = 0
            
        self.signer_histories = {}
        super(ModellingModule, self).__init__(IChannelBasedModel)
        
    def callable(self, input_data):
        """we assume event.data returns a dictionary of the form:
               {'frame': n_x, 
                'articulator1':(a1_x, a1_y),...,'articulator_n':(an_x, an_y)}
        """
        # For the moment it works only with TCIIntervals,
        # defined on the speedbased TrackingModule
        signer_id = input_data[0]
        
        # First time we are entering here for this signer
        if not signer_id in self.signer_histories.keys():
            self.signer_histories[signer_id] = ConcurrentHistory(self.articulators,
                                                                 signer_id)

        input_intervals = input_data[1]
        for articulator in input_intervals.keys():
            interval = input_intervals[articulator]
            
            if interval.is_static_interval:
                # We are creating an state
  
                #average_interval_data = analyser.raw_data[input_interval.upper_limit]
                average_interval_data = {'right_hand' : (0., 0.),
                                         'left_hand' : (0., 0.),
                                         'head' : (0., 0.),
                                         'frame' : 0
                                         }
                # Will hold the entire data set for every frames on this interval
                original_data_set = None
                
                # Calculate average position
                total = len(range(interval.lower_limit, 
                                  interval.upper_limit + 1)) * 1.0

                for frame_n in range(interval.lower_limit, 
                                     interval.upper_limit + 1):
                    
                    # We compile the original data set, in order to 
                    # pass it on to each rule
                    try:
                        original_data_set.append(interval[frame_n])
                    except:
                        original_data_set = interval[frame_n]
                        
                    for key in average_interval_data.keys():
                        if key != "frame":
                            new_tuple = (
                                    average_interval_data[key][0] +\
                                    float(interval[frame_n][key+'_x'])\
                                    / total,
                                    average_interval_data[key][1] +\
                                    float(interval[frame_n][key+'_y'])\
                                    / total
                                    )
                            average_interval_data[key] = new_tuple
                        else:
                            average_interval_data[key] += \
                                            int(interval[frame_n][key]) / total
                
                    if frame_n == interval.upper_limit:
                        # If we are closing, we clean the data
                        average_interval_data['frame'] = int(
                                                    average_interval_data['frame'])

                # Arguments to create state
                rules_kwargs = {'average_data' : average_interval_data,
                                'raw_data' : original_data_set,
                                'frame_interval' : interval.limits(),
                                'articulator' : articulator
                                }
    
                current_state = self.create_state(**rules_kwargs)
                current_state.frame_limits = interval.limits()
                
                # TODO: Check how to do it better, if needed
                current_state.original_tracking = np.array([
                                        average_interval_data['right_hand'],
                                        average_interval_data['left_hand']])

                out_args, vector, _ = current_state.get_members() 
                atoms_held = [out_args[i] for i in range(len(out_args)) if vector[i]==1]

                self.signer_histories[signer_id].append(current_state)
                
                if len(self.signer_histories[signer_id]) >=\
                    self.history_verification_length:
                    # Send history to verificator
                    self.send_to_channels(self.signer_histories[signer_id])
            else:
                # Creates a transition
                last_frame_of_previous_state = interval.lower_limit - 1
                first_frame_of_next_state = interval.upper_limit + 1
                
                # We will need position data from the analysis module
                # so we obtain the tracking data for the limit
                # frame in the received interval
                analyser = zc.getUtility(ISegmentationModule)
                
                origin_raw_data = analyser.numeric_data[
                                            last_frame_of_previous_state :\
                                            last_frame_of_previous_state + 1]
                ending_raw_data = analyser.numeric_data[
                                                first_frame_of_next_state:\
                                                first_frame_of_next_state + 1]
                movement_points = [analyser.numeric_data[i:i+1] for i in range(
                                                last_frame_of_previous_state + 1,
                                                first_frame_of_next_state)
                                   ]
                
#               movement_points = [analyser.raw_data[i] for i in range(
#                                  last_frame_of_previous_state + 1,
#                                  first_frame_of_next_state)
#                                 ]

                trans_kwargs = {'starting_point_tracking' : origin_raw_data,
                                'end_point_tracking' : ending_raw_data,
                                'movement_points' : movement_points,
                                'frame_interval' : interval.limits(),
                                'articulator' : articulator}
                
                transition = self.create_transition(**trans_kwargs)
                transition.frame_limits = interval.limits()
            
                out_args, vector, _ = transition.get_members()
                atoms_held = [out_args[i] for i in range(len(out_args)) if vector[i]==1]

                self.signer_histories[signer_id].append(transition)

        return True
        
    def check_input_compliance(self, input_data):
        # Check that we are still passing a valid id and
        # a series of intervals with panda datasets
        assert isinstance(input_data[0], str)
        assert isinstance(input_data[1], dict)
        
        for key in input_data[1].keys():
            assert isinstance(input_data[1][key], Interval)
        
    def create_state(self, **kwargs):
        '''Create an state in the internal model'''
       
        articulator = kwargs['articulator']
        i = 0
        vector = np.zeros(len(self.ruleset[articulator].posture_rules))
        for rule in self.ruleset[articulator].posture_rules:
            if rule.verify(**kwargs):
                vector[i] = 1
            i += 1

        return ArticulatorState(articulator=articulator,
                            propositions=self.ruleset[articulator].\
                                         get_posture_rule_order(), 
                            vector_repr=vector)
    
    def create_transition(self, **kwargs):
        '''Create a transition in the internal model'''

        articulator = kwargs['articulator']
        i = 0
        vector = np.zeros(len(self.ruleset[articulator].transition_rules))
        for rule in self.ruleset[articulator].transition_rules:
            if rule.verify(**kwargs):
                vector[i] = 1
            i += 1

        return ArticulatorTransition(articulator=articulator,
                                actions=self.ruleset[articulator].\
                                        get_transition_rule_order(),
                                vector_repr=vector)
        
        