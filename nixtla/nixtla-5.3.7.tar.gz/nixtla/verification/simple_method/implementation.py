# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Verification for chains (trees of max. degree 2)

@author: Arturo Curiel
'''

import zope.interface as zi
import zope.component as zc

from nixtla.core.base_module import BaseModule
from nixtla.verification.interface import IVerificationModule
from nixtla.verification.simple_method.markers import ISimpleVerification
from nixtla.verification.simple_method.adapters import FromChannelModel
from nixtla.core.annotation.markers import IAnnotator

from collections import OrderedDict
from nixtla.core.tools import pdlsl


class VerificationModule(BaseModule):
    """Simple verification module"""
    zi.implements(IVerificationModule)
    
    def __init__(self, **args):
        self.annotator = zc.getUtility(IAnnotator)
        self.db = None
        self.agents = None
        # TODO: Parse from db.ini file
#         self.db = OrderedDict({})
#         self.agents = ['right_hand', 'left_hand']
#         E = pos
#         
#         true_left = Atom('True', 'left_hand')
#         true_right = Atom('True', 'right_hand')
#         movement_left = AtomAction("True", 'left_hand')
#         movement_right = AtomAction("True", 'right_hand')
#         movement = movement_left ^ movement_right
#         
#         # Select RIGHT and LEFT hands
#         self.db['RIGHT'] = true_right
#         self.db['LEFT'] = true_left
#         self.db['BOTH'] = self.db['RIGHT'] & self.db['LEFT']
#         
#         left_touches_right = Atom("left_hand touches right_hand", 'left_hand')
#         right_touches_left = Atom("right_hand touches left_hand", 'right_hand')
#         
#         # Select TOUCHING and ~TOUCHING hands
#         self.db['TOUCHING'] =  left_touches_right | right_touches_left
#         self.db['NOTOUCHING'] = ~self.db['TOUCHING']
# 
#         # Select JOINING and SEPARATING hands
#         self.db['JOINING'] = self.db['NOTOUCHING'] & E[movement](self.db['TOUCHING'])
#         self.db['SEPARATING'] = self.db['TOUCHING'] & E[movement](self.db['NOTOUCHING'])
#         
#         # Select TAPs
#         self.db['TAP']= E[self.db['JOINING']](self.db['SEPARATING'])

#        self.annotator.create_tiers(*self.db.keys(), 
#                                    **{'agents':self.agents})
        
        # TODO: Check if still useful
        self.state_count = {}
        self.state_results = {}
        self.formula_count = {}
        
        self.register_module_adapters(FromChannelModel)
        super(VerificationModule, self).__init__(ISimpleVerification)
    
    def callable(self, input_data):
        """we assume input_data has an state to verify
        """

        state = input_data
        
        verified = {}

        for f_name in self.db.keys():
            formula = self.db[f_name]
            # Check if formula is satisfied
            #removable = formula.atomize() - formula.atomize().intersection(
            #                                                state.propositions + ['True'])
            #if f_name == 'TOUCHABLE':
            #    import ipdb;ipdb.set_trace()
            #formula = formula.remove(*list(removable))

            if formula:
                results = state.satisfies(formula) or None
                #if results and f_name == 'RMOVESDOWN':
                #    import ipdb;ipdb.set_trace()
                #    state.satisfies(formula)
            else:
                results = None

            if results:
                verified[f_name] = list(results)
                # DEBUGGING
                # We annotate the subtier                
                self.annotator.group_annotate(str(formula),
                                              str(f_name)+"."+state.driver,
                                              results,
                                              group_invert=True)
                # We annotate the parent tier also,
                # but nameless (to avoid word overlapping)
                self.annotator.group_annotate('',
                                              str(f_name),
                                              results,
                                              group_invert=True)
        try:
            self.state_count[state.tostring()] += 1
        except:
            self.state_count[state.tostring()] = 1
            
        try:
            self.state_results[state.tostring()].add(results)
        except:
            try:
                self.state_results[state.tostring()] = [results]
            except:
                pass
            
        for f_name in verified.keys():
            try:
                self.formula_count[f_name].add(state.tostring())
            except:
                self.formula_count[f_name] = [state.tostring()]
        
        self.send_to_channels(verified)
        return True
    
    def check_input_compliance(self, input_data):
        pass
    
    def read_database(self, ruleset, agents):
        '''Register a database to verify'''
        self.db = OrderedDict({name:ruleset.database[name] for name in \
                                        ruleset.database if \
                                        isinstance(ruleset.database[name], 
                                                   pdlsl.Formula)
                               }
                              )
        self.agents = agents
        self.annotator.create_tiers(*self.db.keys(), 
                                    **{'agents':self.agents})
        
    # DEBUGGING METHODS
    def max_state_count(self):
        max_count = 0
        current_state = None
        for key in self.state_count:
            if self.state_count[key] > max_count:
                max_count = self.state_count[key]
                current_state = key
        return (current_state, max_count)