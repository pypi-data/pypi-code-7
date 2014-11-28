# -*- coding: utf-8 -*-
'''
Created on Mar 3, 2014

This module implements a basic transition class

@author: curiel
'''


from nixtla.core.tools.model.interfaces import ITransition, IState
#import nixtla.core.tools.pdlsl as pdlsl
from nixtla.core.tools.pdlsl import pos, nec

import numpy as np

import zope.interface as zi

class Transition(object):
    zi.implements(ITransition)
    
    def __init__(self, **kwargs):
        self.actions = kwargs['actions']
        self.vector_repr = kwargs['vector_repr']
        
        try:
            self.states = kwargs['children']
        except:
            self.states = []
        
        self.true_values = self.true_valued()
        self.false_values = self.false_valued()
        
        ITransition.validateInvariants(self)

    def __eq__(self, node):
        return np.array_equal(self.vector_repr, 
                              node.vector_repr)

    def __str__(self):
        return str(self.vector_repr).replace("[","").replace("]","").\
            replace(".","").replace("\n","").replace(" ","")
    
    def tostring(self):
        return self.vector_repr.tostring()

    def __contains__(self, atom_action):
        atom_name = str(atom_action)
        
        if atom_name == 'True':
            return True
        elif atom_name == 'False':
            return False
        
        position = self.actions.index(atom_name)
        # If vector marked as 1 in the same position
        if self.vector_repr[position]:
            return True
        else:
            return False
    
    def true_valued(self):
        true_valued = set([])
        for i in range(0, len(self.vector_repr)):
            if self.vector_repr[i]:
                true_valued.add(self.actions[i])
        return true_valued
    
    def false_valued(self):
        false_valued = set([])
        for i in range(0, len(self.vector_repr)):
            if not self.vector_repr[i]:
                false_valued.add(self.actions[i])
        return false_valued
    
    def get_members(self):
        return self.actions, self.vector_repr, self.states

    def connects_to(self, node):
        '''A transition can be connected to other transitions or states'''
        if IState.providedBy(node):
            if not node in self.states:
                self.states.append(node)
                return
        raise TypeError("Not transition: %s" % node)
    
    def __repr__(self, *args, **kwargs):
        repr_str = "\nTransition: \n".format()
        for p in self.true_values:
            repr_str += "\n %s" % p
        return repr_str