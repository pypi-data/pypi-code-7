# -*- coding: utf-8 -*-
'''
Created on Nov 16, 2014

@author: Arturo Curiel
'''

import zope.interface as zi
import zope.component as zc

from nixtla.core.tools.model.interfaces import IRuleSet, IRule
from nixtla.core.module_parser import INixtlaModuleParser

import ConfigParser

from nixtla.core.tools.pdlsl import Atom, AtomAction

from copy import deepcopy
from nixtla.core.tools.database_parser import DatabaseParser


class UndefinedInDomainError(Exception):
    """Gets called when a rule is undefined for a certain domain"""


class BaseRuleSet(object):
    zi.implements(IRuleSet)
    
    def __init__(self, ruleset_path):
        
        self.rules_config = ConfigParser.SafeConfigParser()
        # Preserve Case
        self.rules_config.optionxform=str
        self.rules_config.read(ruleset_path)
        
        self.posture_rules = []
        self.transition_rules = []

        # Checks if we defined variable domains
        if not self.rules_config.has_section('Global') or\
           not self.rules_config.has_section('Posture') or\
           not self.rules_config.has_section('Transition'):
            raise ValueError("Ruleset configuration file is incomplete: %s" %\
                             ruleset_path)

        # Load domains in memory
        aliases = self.rules_config.options('Global')
        self.alias_domains = {}
        self.articulators = None
        for alias in aliases:
            domain = self.rules_config.get('Global', alias)
            domain = domain.replace('[','').\
                            replace(']','').\
                            replace(' ', '').\
                            replace('"', '').\
                            replace('\'','')
            self.alias_domains[alias] = domain.split(',')
            if 'art' in alias:
                self.articulators = self.alias_domains[alias]
        
        # Generates rules
        self.posture_rules = self.generate_rules('Posture')
        self.transition_rules = self.generate_rules('Transition')
        
        self.database = DatabaseParser(self).database
        # TODO: Debugging
#         print ""
#         for rule in self.posture_rules:
#             print rule.__repr__()
#         print ""
#         for rule in self.transition_rules:
#             print rule.__repr__()
#         import ipdb;ipdb.set_trace()

        # Validate ruleset
        IRuleSet.validateInvariants(self)
    
    def get_rule_order(self, rule_list):
        result = []
        for rule in rule_list:
            result.append(str(rule))
        return result
    
    def get_posture_rule_order(self):
        return self.get_rule_order(self.posture_rules)
    
    def get_transition_rule_order(self):
        return self.get_rule_order(self.transition_rules)
    
    def generate_rules(self, section):
        '''Generates every rule in a section'''
        # Gets rule generators
        rule_generators = self.rules_config.options(section)
        global_config = zc.getUtility(INixtlaModuleParser)
        result = []
        for rule in rule_generators:
            # Loads the class specified for each generator
            rule_class = global_config.get_class(self.rules_config.get(
                                                                    section,
                                                                    rule)
                                                )
            # Checks which arguments we must use to create rules
            alias_count = {}
            for alias in self.alias_domains:
                alias_count[alias] = rule.count("$"+alias)
            
            # Adds rule to set
            result += self.create_rule_objects(rule,
                                               rule_class,
                                               alias_count)
        if len(result) == 0:
            raise ValueError("Rules section can't be empty")
        return result
    
    def create_rule_objects(self, generator, generation_class, argument_count, *args):
        # We select only the domains of interest
        aliases = [alias for alias in argument_count if argument_count[alias]!=0]
        aliases.sort()
        result = []

        # Base case
        if len(aliases) == 0:
            
            if generator.count("$") > 0:
                # There are aliases we still haven't resolved
                return []
            
            rule_args = list(args)
            try:
                return [generation_class(generator,
                                         *rule_args)]
            except UndefinedInDomainError:
                return []
            except Exception, e:
                import ipdb;ipdb.set_trace()
                return []

        new_args = list(args)
        new_argument_count = deepcopy(argument_count)
        #for alias in aliases:
        alias = aliases[0]
        new_argument_count[alias]-=1
        for value in self.alias_domains[alias]:
            new_generator = generator.replace('$'+alias, value, 1)
            result += self.create_rule_objects(new_generator, 
                                               generation_class, 
                                               new_argument_count,
                                               *(new_args+[value]))
        return result
    
    # TODO: Eliminate this monster
    def __getitem__(self, articulator):
        class ArticulatorRuleSet(object):
            def __init__(self, 
                         articulator, 
                         posture_rules, 
                         transition_rules):
                self.posture_rules = [rule for rule in posture_rules if\
                                      rule.atom.agent == articulator]
                self.transition_rules = [rule for rule in transition_rules if\
                                         rule.atom.agent == articulator]
            def get_rule_order(self, rule_list):
                result = []
                for rule in rule_list:
                    result.append(str(rule))
                return result
    
            def get_posture_rule_order(self):
                return self.get_rule_order(self.posture_rules)
    
            def get_transition_rule_order(self):
                return self.get_rule_order(self.transition_rules)
        
        return ArticulatorRuleSet(articulator, 
                                  self.posture_rules, 
                                  self.transition_rules)


class BaseRule(object):
    zi.implements(IRule)
    
    def __init__(self, rule_proposition):
        self.atom = rule_proposition
        IRule.validateInvariants(self)

    def isStateRule(self):
        return isinstance(self.atom, Atom)
    
    def isTransitionRule(self):
        return isinstance(self.atom, AtomAction)
    
    def __eq__(self, second_rule):
        return self.atom == second_rule
        
    def verify(self, **kwargs):
        raise ValueError("Not implemented")
    
    def __str__(self):
        return str(self.atom)
    
    def __repr__(self, *args, **kwargs):
        if self.isStateRule():
            rule_type = ": Atom (%s)" % self.atom.agent
        else:
            rule_type = ": AtomAction (%s)" % self.atom.agent
        return str(self.atom) + rule_type