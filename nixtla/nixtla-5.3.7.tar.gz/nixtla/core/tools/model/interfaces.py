# -*- coding: utf-8 -*-
'''
Created on Mar 3, 2014

This module lists the interfaces needed for LTS construction

@author: Arturo CURIEL
'''

from nixtla.core.exceptions import ImplementationError
from nixtla.core.tools.pdlsl import Atom, AtomAction

import zope.interface as zi 

import numpy as np


def check_lts(obj):
    """Verifies LTS values"""
    try:
        if not isinstance(obj.states, dict):
            raise ImplementationError(obj)
        elif not isinstance(obj.transitions, dict):
            raise ImplementationError(obj)
    except:
        ImplementationError(obj)


class ILTS(zi.Interface):
    """A LTS representation"""
    
    states = zi.Attribute("""State list""")
    transitions = zi.Attribute("""Transition list""")
    
    #TODO is this relevant?
    #zi.invariant(check_lts)
    
    
def check_state_transition(obj):
    """Verifies state and transition values"""
    try:
        if not isinstance(obj.vector_repr, np.ndarray):
            raise ImplementationError(obj)
    except:
        raise ImplementationError(obj)
        

class IState(zi.Interface):
    """This interface represents a state in a LTS"""
    
    propositions = zi.Attribute("""List of propositions held in the state""")
    transitions = zi.Attribute("""List of transitions executable from the state""")
    vector_repr = zi.Attribute("""Vector representation of state""")
    
    def satisfies(formula):
        """Method to determine whether a Model satisfies a formula"""
    
    def connects_to(transition):
        """A state can be connected to transitions only"""
    
    zi.invariant(check_state_transition)
        

class ITransition(zi.Interface):
    """This interface represents a transition in a LTS"""
    
    actions = zi.Attribute("""List of parallel actions defining this transition""")
    states = zi.Attribute("""List of nodes reachable by this transition""")
    vector_repr = zi.Attribute("""Vector representation of transition""")
    
    def connects_to(node):
        """A transition can be connected to other transitions or states"""
    
    zi.invariant(check_state_transition)


def check_rule(obj):
    """Verifies rule values"""
    try:
        if not obj.atom:
            # We check that we can generate a name
            raise ImplementationError(obj)
        
        assert isinstance(obj.atom, Atom) or\
               isinstance(obj.atom, AtomAction)
    except:
        raise ImplementationError(obj)


class IRule(zi.Interface):
    """This interface represents a rule to be used in State tagging"""
    
    atom = zi.Attribute("""Rule name generation string""")
    
    def verify(**kwargs):
        """Returns True if arguments satisfy rule, False otherwise"""
    
    zi.invariant(check_rule)

    
def check_ruleset(obj):
    """Verifies ruleset values"""
    try:
        if not isinstance(obj.posture_rules, list) or\
           not isinstance(obj.transition_rules, list):
            raise ImplementationError(obj)
        for rule in obj.posture_rules + obj.transition_rules:
            if not IRule.providedBy(rule):
                raise ImplementationError(obj)
    except:
        raise ImplementationError(obj)


class IRuleSet(zi.Interface):
    """This interface represents a rule set"""
    
    posture_rules = zi.Attribute("""The set of rules to be used for keypostures""")
    transition_rules = zi.Attribute("""The set of rules to be used for transitions""")
    
    zi.invariant(check_ruleset)    