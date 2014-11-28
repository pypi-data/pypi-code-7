# -*- coding: utf-8 -*-
'''
Created on Mar 3, 2014

This module implements a basic state class

@author: curiel
'''


from nixtla.core.tools.model.interfaces import IState, ITransition
import nixtla.core.tools.pdlsl as pdlsl
from nixtla.core.tools.pdlsl import pos, nec, then
from nixtla.core.tools.ordered_set import OrderedSet

import numpy as np
import zope.interface as zi

class State(object):
    '''This is an state'''
    zi.implements(IState)
    
    def __init__(self, **kwargs):
        # propositions is used as an index to find truth value, 
        # so it has to have the same order as vector_repr
        self.propositions = kwargs['propositions']
        self.vector_repr = kwargs['vector_repr']
        try:
            self.transitions = kwargs['transitions']
        except:
            self.transitions = []
        
        self.true_values = self.true_valued()
        self.false_values = self.false_valued()
        
        IState.validateInvariants(self)
    
    def __contains__(self, atom):
        atom_name = str(atom)
        
        if atom_name == 'True':
            return True
        elif atom_name == 'False':
            return False
        
        position = self.propositions.index(atom_name)

        # If vector marked as 1 in the same position
        if self.vector_repr[position]:
            return True
        else:
            return False
            
    def __eq__(self, other_state):
        return np.array_equal(self.vector_repr, 
                              other_state.vector_repr)

    def __str__(self):
        return str(self.vector_repr).replace("[","").replace("]","").\
            replace(".","").replace("\n","").replace(" ","")
            
    def __unstr__(self, simple_str_repr):
        vector_repr = np.zeros(len(simple_str_repr))
        k=0
        for i in simple_str_repr:
            vector_repr[k] = float(i)
            k += 1
        return vector_repr
    
    def tostring(self):
        return self.vector_repr.tostring()
    
    def get_members(self):
        return self.propositions, self.vector_repr, self.transitions
    
    def connects_to(self, transition):
        if ITransition.providedBy(transition):
            if not transition in self.transitions:
                self.transitions.append(transition)
                return
        raise TypeError("Not transition: %s" % transition)
    
    def true_valued(self):
        true_valued = set([])
        for i in range(0, len(self.vector_repr)):
            if self.vector_repr[i]:
                true_valued.add(self.propositions[i])
        return true_valued
    
    def false_valued(self):
        false_valued = set([])
        for i in range(0, len(self.vector_repr)):
            if not self.vector_repr[i]:
                false_valued.add(self.propositions[i])
        return false_valued
    
    def satisfies(self, formula):
        '''Checks satisfaction in the model'''

        # Try boolean values
        if isinstance(formula, bool):
            if formula:
                return OrderedSet([self])
            else:
                return None
            
        is_necessity = isinstance(formula, pdlsl.Necessity)
        is_possibility = isinstance(formula, pdlsl.Possibility)
        
        is_modal = is_necessity or is_possibility
        if is_modal:
            # We will also need the action inside the 
            # formula, since it can be a concatenation
            # or a transitive closure, both of whom
            # are to be interpreted as modal ops.
            action = formula.action
            if is_necessity:
                subformula = formula.terms[0]
                equiv_formula = ~pos[action](~subformula)
                return self.satisfies(equiv_formula)
            elif isinstance(action, pdlsl.Concatenation):
                # We need to check valuation of 
                # [action1][action2]formula
                action1 = action.terms[0]
                action2 = action.terms[1]
                subformula = formula.terms[0]
                
                equiv_formula = pos[action1](pos[action2](subformula))
                return self.satisfies(equiv_formula)
            elif isinstance(action, pdlsl.Concurrence):
                # We need to check valuation of 
                # [action1]formula & [action2]formula
                action1 = action.terms[0]
                action2 = action.terms[1]
                subformula = formula.terms[0]
                
                equiv_formula = pos[action1](subformula) & pos[action2](
                                                                    subformula)
                return self.satisfies(equiv_formula)
            elif isinstance(action, pdlsl.Union):
                # We need to check valuation of 
                # [action1]formula | [action2]formula
                action1 = action.terms[0]
                action2 = action.terms[1]
                subformula = formula.terms[0]
                
                equiv_formula = pos[action1](subformula) | pos[action2](
                                                                    subformula)
                return self.satisfies(equiv_formula)
            elif isinstance(action, pdlsl.TransitiveClosure):
                '''<action*>formula <-> formula | <action><action*>formula
                
                   <action*n>formula <-> <action^(n-1) +...+ action^0>(formula | <action><action*>formula)
                '''
                            
                # TODO: INFINITE CHAIN SATISFACTION DOESN'T WORK
                # WITH TRUE MODELS, ONLY WITH HISTORIES
                stripped_action = action.terms[0]
                subformula = formula.terms[0]
                counter = action.counter
                if counter == 1:
                    # It's a simple action
                    equiv_formula = subformula | pos[stripped_action](
                                                                subformula)
                elif counter > 0 and not isinstance(counter, str):
                    # It's a finite chain
                    counter -= 1
                    equiv_formula = subformula | \
                                        pos[stripped_action](
                                                pos[stripped_action*counter](
                                                                    subformula)
                                                             )
                else:
                    # It's an infinite chain
                    equiv_formula = subformula | \
                                        pos[stripped_action](
                                                pos[stripped_action*counter](
                                                                    subformula)
                                                             )
                closure_op = self.satisfies(equiv_formula)
                if closure_op:
                    closure_op.add(self)
                    return closure_op
                else:
                    return None
            elif isinstance(action, pdlsl.Test):
                # Satisfying tests
                # [f1 == f2?] f3 <-> (f1 <-> f2) -> f3
                #action_subformula = action.terms[0] << action.terms[1]
                # [f1 == f2?] f3 <-> (f1 & f2) -> f3
#                 action_subformula = action.terms[0] & action.terms[1]
#                 state_subformula = formula.terms[0]
#                 equiv_subformula = action_subformula >> state_subformula
                # [A?] B <-> A -> B
                # <A?> ~B <-> A & ~B
                action_subformula = action.terms[0] & action.terms[1]
                if self.satisfies(action_subformula):
                    test_operation = self.satisfies(formula.terms[0])
                    if test_operation:
                        test_operation.add(self)
                        return test_operation
                return None
            elif is_possibility:
                # We will need to read the existing atomic
                # and concurrent transitions to know
                # what's happening.

                subformula = formula.terms[0]
                current_sequence = None

                for transition in self.transitions:
                    # This one here, we expect to change it to 
                    # something as transition.satisfies(action)
                    # and do some searching like with formulas, only
                    # the validation is done in the pdlsl
                    # definition, i.e. not model dependent
                    #if transition.satisfies(action):
#                     if isinstance(action, pdlsl.Empty):
#                         articulator_name = action.terms[1]
#                         empty = True
#                         for action_name in transition.true_values:
#                             if articulator_name in action_name:
#                                 empty = False
#                         if empty:
#                             action = action.terms[0]

                    if str(action) in transition.true_values or str(action) == 'True':
                        for possible_state in transition.states:
                            possible_sequence = possible_state.satisfies(subformula)
                            if possible_sequence:
                                if current_sequence:
                                    if len(current_sequence) < len(possible_sequence):
                                        current_sequence = possible_sequence
                                        current_sequence.add(transition)
                                        current_sequence.add(self)
                                else:
                                    current_sequence = possible_sequence
                                    current_sequence.add(transition)
                                    current_sequence.add(self)
                return current_sequence
            else:
                raise TypeError("can't be a modal pdlsl formula")
        else:
            # Is not modal, propositional valuation in state
            if isinstance(formula, pdlsl.Not):
                inverse_holds = self.satisfies(formula.terms[0])
                if inverse_holds:
                    return None
                else:
                    return OrderedSet([self])
            elif isinstance(formula, pdlsl.Implication):
                term1 = formula.terms[0]
                term2 = formula.terms[1]

                impl_operation = self.satisfies((~term1) | term2)
                if impl_operation:
                    impl_operation.add(self)
                    return impl_operation
                return None
            elif isinstance(formula, pdlsl.DoubleImplication):
                term1 = formula.terms[0]
                term2 = formula.terms[1]
                
                left_side = term1 <<then>> term2
                right_side = term2 <<then>> term1
                
                db_impl_operation = self.satisfies(left_side & right_side)
                if db_impl_operation:
                    db_impl_operation.add(self)
                    return db_impl_operation
                return None
            elif isinstance(formula, pdlsl.And):
                term1 = formula.terms[0]
                term2 = formula.terms[1]
                
                left_side = self.satisfies(term1)
                right_side = self.satisfies(term2)
                
                and_operation = left_side and right_side
                if and_operation:
                    if len(left_side) > len(right_side):
                        left_side.add(self)
                        return left_side
                    else:
                        right_side.add(self)
                        return right_side

                # One of them None
                return None
            elif isinstance(formula, pdlsl.Or):
                term1 = formula.terms[0]
                term2 = formula.terms[1]
                
                left_side = self.satisfies(term1)
                right_side = self.satisfies(term2)
                
                # OR comparison
                or_operation = left_side or right_side
                if or_operation:
                    if left_side and right_side:
                        if len(left_side) > len(right_side):
                            left_side.add(self)
                            return left_side
                        else:
                            right_side.add(self)
                            return right_side
                    else:
                        or_operation.add(self)
                        return or_operation

                # Both None 
                return None
            elif isinstance(formula, pdlsl.Atom):
                if formula in self:
                    return OrderedSet([self])
                else:
                    return None
            else:
                raise TypeError("pdlsl formula type not found" + str(formula.__class__))
            
    def __repr__(self, *args, **kwargs):
        repr_str = "\nState: \n".format()
        for p in self.true_values:
            repr_str += "\n %s" % p
        return repr_str