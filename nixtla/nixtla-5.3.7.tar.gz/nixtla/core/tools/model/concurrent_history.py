# -*- coding: utf-8 -*-
'''
Created on Jul 10, 2014

LTS-based concurrent history data structure

@author: Arturo CURIEL
'''

from collections import deque
from nixtla.core.tools.ordered_set import OrderedSet
import nixtla.core.tools.pdlsl as pdlsl

from nixtla.core.tools.model.interfaces import ILTS, IState, ITransition
from nixtla.core.tools.model.state import State
from nixtla.core.tools.model.transition import Transition

import zope.interface as zi
import zope.component as zc

from nixtla.core.tools.pdlsl import AtomAction

from zope.interface.declarations import alsoProvides
from nixtla.core.annotation.markers import IAnnotator


class ArticulatorLTSFields(object):
        
    def __init__(self, **kwargs):
        '''Instance of State with temporal tags'''

        try:
            self.history = kwargs['history']
        except:
            self.history = None
    
        try:
            self.frame_limits = kwargs['frame_limits']
        except:
            self.frame_limits = (0, 0)
            
        try:
            self.driver = kwargs['articulator']
        except:
            self.driver = None
            
            
        self.original_tracking = None
        
    def __repr__(self, *args, **kwargs):
        return "\nArticulatorLTSFields:\nFrame Limits: {0}\nArticulator: {1}".\
                                                          format(str(self.frame_limits),
                                                                 self.driver)
    

class PosibilitySatisfaction(object):
    
    def get_next_middle_transition(self, articulator):
        '''Gets the next transition of self state or a transition parallel
        to it (if it exists)'''
        
        if len(self.transitions) == 0:
            return None, None
        
        next_transition = self.transitions[0]
        overlappers = self.history.who_overlaps(next_transition.frame_limits, 
                                                ITransition)
        try:
            interest_object = overlappers[articulator].pop_left()
#             if self.history.get_overlap_total(
#                                              interest_object.frame_limits,
#                                              self.frame_limits
#                                              ) > 0:
#                 # We take the next one, because the previous one wasn't 
#                 # strictly "after"
#                 interest_object = overlappers[articulator].pop_left()
            return (interest_object,
                    self.history.overlapping_frame_limit(
                                                interest_object.frame_limits,
                                                next_transition.frame_limits
                                                )
                    )
        except:
            return None, None

    def get_closer_state(self, frame_limits):
       
        transitions_in_interval = self.history.who_overlaps(frame_limits,
                                                            ITransition)
        closer_state = None
        for articulator in transitions_in_interval.keys():
            try:
                interest_object = transitions_in_interval[articulator]\
                                                                    .pop_left()
                try:
                    interest_object = interest_object.states[0]
                except:
                    return None
                if not closer_state:
                    closer_state = interest_object
                elif interest_object.frame_limits[0] < closer_state.frame_limits[0]:
                    closer_state = interest_object
            except:
                pass
        return closer_state
    
    def process_atomaction(self, formula):
        # We just pass the formula to the single Transition
        # contained in the list of transitions
        if len(self.transitions) > 1:
            raise ValueError("An ArticulatorState can't have more than one\
                              ArticulatorTransition")
        elif len(self.transitions) == 0:
            return None
        
        check_subformula = False
        if self.transitions[0].driver == formula.action.agent:
            # k1 |= [m1]k2 where k1.agent == m1.agent
            # Same agent, we are verifying satisfaction on our own history.
            if str(formula.action) in self.transitions[0].true_values or\
               str(formula.action) == 'True':
                check_subformula = True
                chosen_transition = self.transitions[0]
                ct_limits = chosen_transition.frame_limits
        else:
            # k1 |= [m1]k2 where k1.agent != m1.agent
            # Different agent, we check the first transition overlapping with
            # current agent's transition
            chosen_transition, ct_limits = self.get_next_middle_transition(
                                                        formula.action.agent
                                                        )
            if chosen_transition:
                # We found an overlapping transition, we check its values.
                if str(formula.action) in chosen_transition.true_values or\
                   str(formula.action) == 'True':
                    check_subformula = True
        
        # We get the closer state in the within the limits of self's
        # transition
        closer_state = self.get_closer_state(self.transitions[0].frame_limits)
        if check_subformula:
            # Action is good!
            
            # If a formula has info about a single agent,
            # we choose the next state in this agent's history 
            # history, if not, we risk of losing info when 
            # k1.agent1 |= [m1.agent2] k2.agent2 or
            # similar cases
            subformula_agents = formula.terms[0].agents() 
            if len(subformula_agents) == 1:
                # We use the only agent to select next state
                if chosen_transition.driver in subformula_agents:
                    # The agent of the state and the movement are the same
                    # m1.agent == k2.agent
                    try:
                        state_after_transition = chosen_transition.states[0]
                    except:
                        return None
                else:
                    # Not the case, we get the closer state
                    if not closer_state:
                        return None
                    
                    if closer_state.driver in subformula_agents:
                        state_after_transition = closer_state
                    else:
                        # The closer state couldn't possibly satisfy
                        # formula
                        return None
            else:
                # We are looking for a static overlap,
                # so we just use the closer state.
                if not closer_state:
                    return None
                
                state_after_transition = closer_state
            
            # We verify subformula on the chosen state
            subformula_operation = state_after_transition.satisfies(
                                                    formula.terms[0]
                                                    )
            if subformula_operation:
                # We have satisfaction, we complete annotation
                # with the overlapping movement frames.
                
                # We assure that the transition limits are
                # consistent
                oat_limits = (ct_limits[0],
                              state_after_transition.frame_limits[0] - 1)
                
                # We create a representation of the used transition
                pseudo_transition = ArticulatorLTSFields(
                            frame_limits=oat_limits,
                            articulator=state_after_transition.driver
                            )
                alsoProvides(pseudo_transition, ITransition)
                subformula_operation.add(pseudo_transition)
                # TODO: Check that adding self is the way to go or not
                #if len(self.history.combine_interval_sets(subformula_operation,
                #                                                {self})) < 3:
                #    import ipdb;ipdb.set_trace()
                subformula_operation = self.history.combine_interval_sets(subformula_operation,
                                                                          {self})
            return subformula_operation
        return None
            
    def process_union(self, formula):
        # Process a union formula [a1^a2]phi
        subformula = formula.terms[0]
        eq_formula1 = pdlsl.pos[formula.action.terms[0]](subformula)
        eq_formula2 = pdlsl.pos[formula.action.terms[1]](subformula)
        
        # In general, it's just an Or: [a1^a2]phi = [a1]phi | [a2]phi
        return self.satisfies(eq_formula1 | eq_formula2)
    
    def process_single_step_sequence(self, formula):
        # Process a single step in a sequence formula like [a1;a2]phi
        subformula = formula.terms[0]
        first_action = formula.action.terms[0]
        second_action = formula.action.terms[2]
        equiv_formula = pdlsl.pos[first_action](pdlsl.pos[second_action](subformula))
        return self.satisfies(equiv_formula)
    
    def process_closure(self, formula):
        # [a**i]k executes a until k, at least i times
        if formula.action.counter == 1:
            # We search the definitive step were |= [a]k
            step_formula = pdlsl.pos[formula.action.terms[0]](formula.terms[0])
            first_step_result = self.satisfies(step_formula)
            if first_step_result:
                # This is it, send a well-formed sequence (including self)
                return self.history.combine_interval_sets(first_step_result,
                                                          {self})
            else:
                # The immediate step was not it, we try to go farther
                equiv_formula = pdlsl.pos[formula.action.terms[0]](formula)
                results = self.satisfies(equiv_formula)
                if results:
                    # We're out of the woods
                    return self.history.combine_interval_sets(results,
                                                              {self})
        else:
            # We are not there yet
            sub_formula = pdlsl.pos[formula.action.terms[0]**(
                                                formula.action.counter-1)](
                                                            formula.terms[0])
            equiv_formula = pdlsl.pos[formula.action.terms[0]](sub_formula)
            results = self.satisfies(equiv_formula)
            if results:
                return self.history.combine_interval_sets(results,
                                                          {self})
        return None
    
    def assert_test(self, formula):
        formula_to_test = formula.terms[0]
        #subformula = formula.terms[0]
        result = self.satisfies(formula_to_test)
        if result:
            return True
        return False
    
    def process_concurrency(self, formula):
        # Assumes that formula.action == alpha1 // alpha2
        if isinstance(formula.action.terms[0], pdlsl.Test):
            if isinstance(formula.action.terms[1], pdlsl.Test):
                # Have to rethink it
                import ipdb;ipdb.set_trace()
                return None
            else:
                # First is a test, second an action
                return self.process_test_concurrent_action(
                                                    formula.action.terms[0],
                                                    formula.action.terms[1],
                                                    formula.terms[0])
        else:
            if isinstance(formula.action.terms[0], pdlsl.Test):
                # first is an action, second is a Test
                return self.process_test_concurrent_action(
                                                    formula.action.terms[1],
                                                    formula.action.terms[0],
                                                    formula.terms[0])
            else:
                # Both actions
                return self.process_action_action(formula)
        raise TypeError("Invalid formula type: {0}".format(str(type(formula))))
    
    def process_test_concurrent_action(self, 
                                       formula_to_test,
                                       interest_action,
                                       subformula):

        if not isinstance(formula_to_test, pdlsl.Test):
            raise TypeError("Not a proper formula of type [TEST//ACTION]SubF")
        
        test_agents = formula_to_test.agents()
        action_agents = interest_action.agents()
        
        if len(test_agents) == 1 or len(action_agents) == 1:
            action_agent = action_agents.pop()
            test_agent = test_agents.pop()
            if action_agent == test_agent:
                return None
        else:
            return None
        #test_result = self.satisfies(pdlsl.pos[formula_to_test](subformula))
        test_result = self.satisfies(formula_to_test.terms[0])
        running_result = test_result
        correct_action_found = False
        if test_result:
            interest_frames = (test_result.peek().frame_limits[0],
                               test_result.peek_left().frame_limits[1])
            overlappers = self.history.who_overlaps(interest_frames,
                                                    IState)
            if not action_agent in overlappers.keys():
                return None
            
            for state in overlappers[action_agent]:
                subformula_result = state.satisfies(pdlsl.pos[interest_action](
                                                                    subformula
                                                                    )
                                                    )
                if subformula_result.peek_left().frame_limits[1] > \
                   interest_frames[1]:
                    subformula_result = None

                if subformula_result:
                    #if self.driver == 'left_hand':
                        #import ipdb;ipdb.set_trace()
                    intersect = self.history.get_interval_intersection(
                                                        subformula_result,
                                                        test_result)
                    running_result = self.history.combine_interval_sets(
                                                            running_result,
                                                            intersect,
                                                            cover_holes=True)
                    correct_action_found = True
                    
        if correct_action_found:
            if len(running_result) > 0:
                return running_result
        return None
            
    def process_action_action(self, formula):
        # We take it simply as |= [a1//a2]k1 iff [a1]k1 & [a2]k1
        subformula = formula.terms[0]
        a1 = formula.action.terms[0]
        a2 = formula.action.terms[1]
        equiv_formula1 = pdlsl.pos[a1](subformula)
        equiv_formula2 = pdlsl.pos[a2](subformula)
        return self.satisfies(equiv_formula1 & equiv_formula2)
    

class ArticulatorState(State, PosibilitySatisfaction, ArticulatorLTSFields):
    
    def __init__(self, **kwargs):
        '''Instance of State with temporal tags'''
        State.__init__(self, **kwargs)
        ArticulatorLTSFields.__init__(self, **kwargs)

    def __repr__(self, *args, **kwargs):
        return State.__repr__(self) +\
            "\n Frame Limits: {0}".format(self.frame_limits) +\
            "\n Articulator: {0}".format(self.driver)
    
    def satisfies(self, formula):
        '''Checks satisfaction for ArticulatorState objects'''

        # Try boolean values
        if isinstance(formula, bool):
            if formula:
                return OrderedSet([self])
            else:
                return None
        
        is_possibility = isinstance(formula, pdlsl.Possibility)
        is_sequence = isinstance(formula, pdlsl.Sequence)
        is_until = isinstance(formula, pdlsl.Until)
        is_atomic_formula = isinstance(formula, pdlsl.Atom)
        
        if is_possibility:
            action = formula.action
            # We are only considering AtomAction verification
            is_atomaction = isinstance(action, pdlsl.AtomAction)
            is_concurrency = isinstance(action, pdlsl.Concurrence)
            is_union = isinstance(action, pdlsl.Union)
            is_closure = isinstance(action, pdlsl.TransitiveClosure)
            is_test = isinstance(action, pdlsl.Test)
            if is_atomaction:
                return self.process_atomaction(formula)
            elif is_concurrency:
                return self.process_concurrency(formula)
            elif is_union:
                return self.process_union(formula)
            elif is_closure:
                return self.process_closure(formula)
            elif is_test:
                if self.assert_test(action):
                    # Test is true, get results
                    return self.satisfies(formula.terms[0])
        elif is_atomic_formula:
            # We examine the atom to discover if we have to search
            # the truth in another channel
            if formula.agent != self.driver:
                overlappers = self.history.who_overlaps(self.frame_limits,
                                                        IState)
                results = OrderedSet([])
                if not formula.agent in overlappers.keys():
                    return None
                
                for state in overlappers[formula.agent]:
                    if state.satisfies(formula):
                        interest_interval = self.history.\
                                                overlapping_frame_limit(
                                                            state.frame_limits,
                                                            self.frame_limits
                                                            )
                        results.add(ArticulatorLTSFields(frame_limits=interest_interval,
                                                         articulator=state.driver))
                if len(results) > 0:
                    for s in results:
                        alsoProvides(s, IState)
                    return results
        elif is_sequence:
            # Check if the formula is intended to be a sequence
            first_in_seq = formula.terms[0]
            second_in_seq = formula.terms[1]
            
            first_results = self.satisfies(first_in_seq)
            if first_results:
                last_state = first_results.peek_left()
                try:
                    second_results = last_state.satisfies(second_in_seq)
                except:
                    last_state = self.get_closer_state(last_state.frame_limits)
                    if last_state:
                        second_results = last_state.satisfies(second_in_seq)
                    else:
                        second_results = None
                if second_results:
                    return self.history.combine_interval_sets(first_results,
                                                              second_results)
            return None
        elif is_until:
            formula_to_repeat = formula.terms[0]
            results = self.satisfies(formula_to_repeat)
            if results:
                return self.history.combine_interval_sets(results,
                                                          {})
            else:
                try:
                    more_results = self.transitions[0].states[0].satisfies(formula)
                except:
                    return None
                    
                if more_results:
                    more_results.add(self.transitions[0])
                    more_results.add(self)
                    return self.history.combine_interval_sets(more_results,
                                                              {self})
            return None

        elif isinstance(formula, pdlsl.And):
            # We need to enter here in order to correctly select each interval
            first_results = self.satisfies(formula.terms[0])
            second_results = self.satisfies(formula.terms[1])

            if first_results and second_results:
                # We get the intersection
                # TODO: Check if this will always work
#                 if isinstance(formula.terms[0], pdlsl.Possibility) and\
#                      isinstance(formula.terms[1], pdlsl.Possibility):
#                     first_results_cover = first_results.peek_left().frame_limits[1]\
#                                           - first_results.peek().frame_limits[0]
#                     second_results_cover = second_results.peek_left().frame_limits[1]\
#                                           - second_results.peek().frame_limits[0]
#                     longest = first_results if first_results_cover >= \
#                                                 second_results_cover \
#                                             else second_results
#                     return longest
                if isinstance(formula.terms[0], pdlsl.Possibility) or\
                   isinstance(formula.terms[1], pdlsl.Possibility) or\
                   isinstance(formula.terms[0], pdlsl.Until) or\
                   isinstance(formula.terms[1], pdlsl.Until):
                    return self.history.combine_interval_sets(first_results,
                                                              second_results)
                return self.history.get_interval_intersection(first_results,
                                                              second_results)
            return None
        elif isinstance(formula, pdlsl.Or):
            # We need to enter here in order to correctly select each interval
            first_results = self.satisfies(formula.terms[0])
            second_results = self.satisfies(formula.terms[1])

            if first_results and second_results:
                return self.history.combine_interval_sets(first_results,
                                                          second_results)
            else:
                results = first_results or second_results
                if results:
                    return self.history.combine_interval_sets(results,
                                                              {})
            return None

        # If it is not a possibility modal formula, nor an external, we use the original 
        # satisfaction method to calculate
        try:
            return super(ArticulatorState, self).satisfies(formula)
        except ValueError, e:
            # This happens whenever the satisfaction procedure doesn't 
            # find an atom inside an state, mostly because 
            # atom.agent != state.driver
            return None

    
class ArticulatorTransition(Transition, ArticulatorLTSFields):
    
    def __init__(self, **kwargs):
        '''Instance of Transition with temporal tags'''
        Transition.__init__(self, **kwargs)
        ArticulatorLTSFields.__init__(self, **kwargs)
    
    def __repr__(self, *args, **kwargs):
        return super(ArticulatorTransition, self).__repr__(*args, **kwargs) +\
            "\n Frame Limits: {0}".format(self.frame_limits) +\
            "\n Articulator: {0}".format(self.driver)


class ConcurrentHistory(object):
    '''Enumerated sequence of states/transitions, saved as concurrent 
    sequences'''
    zi.implements(ILTS)
    
    def __init__(self, articulators, 
                 signer_id='Signer0'):
        '''Representation of the global concurrent: each state is induced by 
          a the set of concurrent static postures. Everything else is taken
          as a transition in the global history. Regardless, individual
          states exist in the underlying channel, saving unchanged 
          information.'''
        
        self.channels = {}
        self.node_index = {}
        self.states = {}
        self.transitions = {}
        self.merged_states = 0
        for articulator in articulators:
            self.channels[articulator] = deque()
            self.states[articulator] = []
            self.transitions[articulator] = []
            self.node_index[articulator] = {}
        self.articulators = articulators
        
        self.signer_id = signer_id
        
        # This index will map frames to MergedStates
        self.merged_state_index = {}
        
        #DEBUGGING
        self.elan_annotation = zc.getUtility(IAnnotator)
                               #ElanAnnotation(input_file_path=None, 
                               #               author="Nixtla", 
                               #               output_file_path=elan_path)
        #DEBUGGING
    
    def __len__(self):
        return max([len(self.channels[articulator]) for \
                    articulator in self.channels.keys()])
    
    def append(self, obj):
        '''Appends a new object to the sequence'''
        
        # We set a reference to the global history, for satisfaction
        # purposes
        obj.history = self
        if IState.providedBy(obj):
            # Regardless of merging, the state is part of the individual 
            # history
            inserted = False
            try:
                if ITransition.providedBy(self.channels[obj.driver][-1]):
                    self.channels[obj.driver][-1].connects_to(obj)
                    self.channels[obj.driver].append(obj)
                    self.states[obj.driver].append(obj)
                    inserted = True
            except IndexError:
                # The sequence was empty, let's just insert
                self.channels[obj.driver].append(obj)
                self.states[obj.driver].append(obj)
                inserted = True
            except Exception, e:
                raise e
            #DEBUGGING
            self.elan_annotation.to_keyposture(obj)
            #DEBUGGING
            
            try:
                # Create an index
                if inserted:
                    self.node_index[obj.driver].update(
                                dict.fromkeys(range(*obj.frame_limits)\
                                              + [obj.frame_limits[1]],
                                              obj)
                )
            except Exception, e:
                raise ValueError("Problem Creating Node Index")

        elif ITransition.providedBy(obj):
            # We are inserting a transition in local history
            inserted = False
            try:
                if IState.providedBy(self.channels[obj.driver][-1]):
                    
                    # Tell the previous state that we are 
                    self.channels[obj.driver][-1].connects_to(obj)
                    self.channels[obj.driver].append(obj)
                    self.transitions[obj.driver].append(obj)
                    inserted = True

            except IndexError:
                # The sequence was empty, let's just insert
                #raise ValueError("First insert must be an state, not %s"  \
                #                 % str(type(obj)))
                self.channels[obj.driver].append(obj)
                self.transitions[obj.driver].append(obj)
                inserted = True
            except Exception, e:
                raise e
            #DEBUGGING
            self.elan_annotation.to_movement(obj)
            #DEBUGGING
            try:
                # Create an index
                if inserted:
                    self.node_index[obj.driver].update(
                                dict.fromkeys(range(*obj.frame_limits)\
                                              + [obj.frame_limits[1]],
                                              obj)
                    )
            except Exception, e:
                raise ValueError("Problem Creating Node Index")
                
        else:
            raise TypeError("Not State nor Transition")
        
    def get_overlap_total(self, a, b):
        count = 0
        b_members = range(b[0], b[1]+1)
        for a_member in range(a[0], a[1]+1):
            if a_member in b_members:
                count+=1
        return count
    
    def is_overlap(self, a, b):
        if a[1] < b[0] or b[1] < a[0]:
            return False
        else:
            return True
        
    def query(self, atom_p):
        query_results = []
        for state in self.states:
            if state.satisfies(atom_p):
                query_results.append(state)
        return query_results

    def get_obj_for_frame(self, articulator, frame):
        try:
            return self.node_index[articulator][frame]
        except:
            pass
            
    def who_overlaps(self, frame_limits, specific_interface=None):
        result = {}
        for i in range(frame_limits[0],
                       frame_limits[1] + 1):
            for channel in self.articulators:
                overlapped_obj = self.get_obj_for_frame(channel, i)
                if specific_interface:
                    if not specific_interface.providedBy(overlapped_obj):
                        overlapped_obj = None
                        
                if overlapped_obj:
                    try:
                        result[channel].add(overlapped_obj)
                    except:
                        result[channel] = OrderedSet([overlapped_obj])
        return result

    def merge_double_list(self, first_list, second_list, articulator, reverse=False, marker_interface=IState):
        result = []
        for first_interval in first_list:
            if marker_interface.providedBy(first_interval):
                for second_interval in second_list:
                    if marker_interface.providedBy(first_interval):
                        new_interval = self.overlapping_frame_limit(
                                                first_interval.frame_limits, 
                                                second_interval.frame_limits
                                                )
                        if new_interval:
                            result.append(ArticulatorLTSFields(
                                                    frame_limits=new_interval,
                                                    articulator=articulator)
                                          )
                            alsoProvides(result[-1], marker_interface)
        result.sort(key=lambda interval: interval.frame_limits[0], reverse=reverse)
        return OrderedSet(result)

    def combine_interval_sets(self, first_set, second_set, cover_holes=True):
        # Combine two OrderedSet interval lists into a single, uninterrupted one

        combined = [elem for elem in set(first_set).union(set(second_set))]
        if len(combined) <= 1:
            # single element, can't really merge...
            return OrderedSet(combined)
        combined.sort(key=lambda x: x.frame_limits[0], reverse=True)
        result = []
        first = combined.pop()
        second = None
        while len(combined) > 0:
            second = combined.pop()
            if self.get_overlap_total(first.frame_limits,
                                      second.frame_limits) > 0:
                # They overlap, we merge them
                new_frame_range = (min(first.frame_limits[0],
                                       second.frame_limits[0]),
                                   max(first.frame_limits[1],
                                       second.frame_limits[1]))
                new_interval = ArticulatorLTSFields(
                                                frame_limits=new_frame_range
                                                )
                try:
                    if self.get_overlap_total(result[-1].frame_limits,
                                              new_interval.frame_limits) > 0:
                        # if the last interval is overlapping, we just update
                        # with the new one
                        result.pop()
                except IndexError:
                    # result is empty, just ignore
                    pass
                result.append(new_interval)
                first = new_interval
                second = None
            elif (first.frame_limits[1] + 1 != second.frame_limits[0]) and\
                cover_holes:
                # They don't overlap, and they are too separated from 
                # one another 
                new_frame_range = (first.frame_limits[1] + 1,
                                   second.frame_limits[0] - 1)
                new_interval = ArticulatorLTSFields(
                                                frame_limits=new_frame_range
                                                )
                result.append(first)
                result.append(new_interval)
                first = second
            else:
                # They are correctly separated, we insert the first as-is
                # and save the second for further checking
                result.append(first)
                first = second
        
        if second:
            result.append(second)
        result.reverse()
        return OrderedSet(result)
    
    def get_interval_intersection(self, first_set, second_set):
        # We assume that first_set and second_set don't have holes
        combined = []
        for first_interval in first_set:
            for second_interval in second_set:
                if self.get_overlap_total(first_interval.frame_limits,
                                          second_interval.frame_limits) > 0:
                    new_limits = (max(first_interval.frame_limits[0],
                                        second_interval.frame_limits[0]),
                                    min(first_interval.frame_limits[1],
                                        second_interval.frame_limits[1]))
                    combined.append(ArticulatorLTSFields(frame_limits=new_limits))
        return self.combine_interval_sets(combined, {}, cover_holes=False)
    
    def popfirststate(self):
        max_value = 0
        max_articulator = None
        for articulator in self.channels.keys():
            if len(self.channels[articulator]) > max_value:
                max_value = len(self.channels[articulator])
                max_articulator = articulator
        if max_value != 0:
            state = self.channels[max_articulator].popleft()
            while not IState.providedBy(state):
                state = self.channels[max_articulator].popleft()
            return state
        raise KeyError("Empty history")
    
    def overlapping_frame_limit(self, a, b):
        results = []
        b_members = range(b[0], b[1]+1)
        for a_member in range(a[0], a[1]+1):
            if a_member in b_members:
                results.append(a_member)
        if len(results) <= 0:
            return None
        else:
            return (results[0], results[-1])
    
    # DEBUGGING
    def is_valid_sequence(self, seq):
        '''Checks if the resulting sequence of a satisfaction procedure 
        is a valid sequence'''
        seq = [elem for elem in seq]
        first = seq.pop()
        while len(seq) > 0:
            second = seq.pop()
            if first.frame_limits[1] +1 != second.frame_limits[0]:
                return False
            first = second
        return True