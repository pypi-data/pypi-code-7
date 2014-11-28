# -*- coding: utf-8 -*-
'''
Created on Nov 18, 2014

@author: Arturo Curiel
'''

import ply.yacc as yacc
import ply.lex as lex
import ply.ctokens as ctokens

import ConfigParser
import StringIO
from nixtla.core.tools.pdlsl import Atom, AtomAction
from nixtla.core.tools import pdlsl


class PDLSLLexer(object):
    
    tokens = ('PHI_BINOPERATOR',
              'PI_BINOPERATOR',
              'PHI_UNIOPERATOR',
              'PI_UNIOPERATOR',
              'ATOM',
              'ATOMACTION',
              'ARTICULATOR',
              'LPAREN',
              'RPAREN',
              'LBRACKET',
              'RBRACKET',
              'ALIAS')
    
    t_ignore  = ' \t'
    
    t_PHI_BINOPERATOR = r'&|\|{2}|->|<->'
    t_PI_BINOPERATOR = r'//|\^|;'
    t_PHI_UNIOPERATOR = ctokens.t_NOT
    t_PI_UNIOPERATOR = r'\?|\*{2}[0-9]+'
    t_ATOM = r'ATOM[0-9]+'
    t_ATOMACTION = r'ACTION[0-9]+'
    t_ARTICULATOR = r'ART[0-9]+'
    t_LPAREN = ctokens.t_LPAREN
    t_RPAREN = ctokens.t_RPAREN
    t_LBRACKET = ctokens.t_LBRACKET
    t_RBRACKET = ctokens.t_RBRACKET
    
    def __init__(self, 
                 aliases):
        
        self.t_ALIAS = r"|".join(aliases)
        self.lexer = lex.lex(module=self)

    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def input(self, data):
        self.lexer.input(data)
        
    # DEBUGGING
    def tokenize(self, data):
        'Debug method!'
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if tok:
                yield tok
            else:
                break

    def print_tokens(self, data):
        for token in self.tokenize(data):
            print token


class DatabaseParser(object):
    '''Parses the formulae section of a rules.ini file'''
    
    precedence = (
                  ('right', 'PHI_UNIOPERATOR'),
                  ('left', 'PI_UNIOPERATOR'),
                  ('left', 'PI_BINOPERATOR'),
                  ('left', 'PHI_BINOPERATOR')
                  )
    
    def __init__(self, ruleset):
        
        if not ruleset.rules_config.has_section('Formulae'):
            raise ValueError("Couldn't parse formulae to annotate")
        
        formulae_options = ruleset.rules_config.options('Formulae')
        if 'database_file' in formulae_options:
            database_ini = ruleset.rules_config.get('Formulae', 'database_file')
            ini_str = '[Formulae]\n' + open(database_ini, 'r').read()
            ini_fp = StringIO.StringIO(ini_str)
            config = ConfigParser.SafeConfigParser()
            config.optionxform=str
            config.readfp(ini_fp)
        else:
            config = ruleset.rules_config
        
        self.atoms =  {str(rule):rule.atom for rule in ruleset.posture_rules}
        self.actions =  {str(rule):rule.atom for rule in ruleset.transition_rules}
        
        # TODO: Here to not add articulators
        self.atom_index = self.atoms.keys()
        
        self.articulators = None
        for alias in ruleset.alias_domains.keys():
            if "art" in alias:
                # we take this as an articulator
                self.articulators = ruleset.alias_domains[alias]
                for articulator in self.articulators:
                    self.atoms[articulator] = Atom('True', articulator)
                    self.actions[articulator+"_movement"] = AtomAction('True', articulator)
        
        # TODO: Here to add articulator_movement
        self.action_index = self.actions.keys()

        self.definitions = config.options("Formulae")
        
        # Start parser
        self.lexer = PDLSLLexer(self.definitions)
        
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, write_tables=0, debug=False)
        
        self.database = {}
        for option in self.definitions:
            string_to_parse = self.substitute_atoms(config.get("Formulae", 
                                                               option))
            self.database[option] = self.parser.parse(string_to_parse)

    def p_error(self,pe):
        print 'Error!'
        print pe
        print

    def p_expression_isaction(self, p):
        '''expression : action'''
        p[0] = p[1]

    def p_expression_alias(self, p):
        '''expression : ALIAS'''
        p[0] = self.database[p[1]]

    def p_expression_atom(self, p):
        '''expression : ATOM'''
        entry = int(p[1].replace("ATOM",""))
        atom_name = self.atom_index[entry]
        p[0] = self.atoms[atom_name]
        
    def p_articulator_expression_phi(self, p):
        '''expression : ARTICULATOR PHI_BINOPERATOR ARTICULATOR
                      | ARTICULATOR PHI_BINOPERATOR expression
                      | expression PHI_BINOPERATOR ARTICULATOR'''
        
        if 'ART' in p[1]:
            p[1] = self.get_articulator_atom(p[1])
        if 'ART' in  p[3]:
            p[3] = self.get_articulator_atom(p[3])
        
        p[0] = self.calculate_formula(p[2], p[1], p[3])

    def p_articulator_uniexpression_phi(self, p):
        '''expression : PHI_UNIOPERATOR ARTICULATOR'''
        if p[2] in self.articulators:
            p[2] = self.get_articulator_atom(p[2])

        p[0] = self.calculate_formula(p[1], p[2])
    
    def p_uniexpression_phi(self, p):
        '''expression : PHI_UNIOPERATOR expression'''
        p[0] = self.calculate_formula(p[1], p[2])
        
    def p_binexpression_phi(self, p):
        '''expression : expression PHI_BINOPERATOR expression'''
        p[0] = self.calculate_formula(p[2], p[1], p[3])
    
    def p_expression_modal(self, p):
        '''expression : LBRACKET action RBRACKET LPAREN expression RPAREN
                      | LBRACKET expression RBRACKET LPAREN expression RPAREN'''
        p[0] = pdlsl.pos[p[2]](p[5])
    
    def p_expression_group(self, p):
        '''expression : LPAREN expression RPAREN'''
        p[0] = p[2]
    
    def p_action_alias(self, p):
        '''action : ALIAS'''
        p[0] = self.database[p[1]]
        
    def p_action_atom(self, p):
        '''action : ATOMACTION'''
        entry = int(p[1].replace("ACTION",""))
        action_name = self.action_index[entry]
        p[0] = self.actions[action_name]
    
    def p_articulator_binaction_pi(self, p):
        '''action : ARTICULATOR PI_BINOPERATOR ARTICULATOR
                  | ARTICULATOR PI_BINOPERATOR action
                  | action PI_BINOPERATOR ARTICULATOR'''
        
        if 'ART' in p[1]:
            p[1] = self.get_articulator_atomaction(p[1])
        if 'ART' in  p[3]:
            p[3] = self.get_articulator_atomaction(p[3])
        
        p[0] = self.calculate_action(p[2], p[1], p[3])

    def p_articulator_uniaction_pi(self, p):
        '''action : ARTICULATOR PI_UNIOPERATOR'''
        
        if 'ART' in p[1]:
            p[1] = self.get_articulator_atomaction(p[1])
        
        p[0] = self.calculate_action(p[2], p[1])

    def p_uniaction_pi(self, p):
        '''action : action PI_UNIOPERATOR'''
        p[0] = self.calculate_action(p[2], p[1])

    def p_binaction_pi(self, p):
        '''action : action PI_BINOPERATOR action'''
        p[0] = self.calculate_action(p[2], p[1], p[3])
        
    def p_action_group(self, p):
        '''action : LPAREN action RPAREN'''
        p[0] = p[2]
    
    def calculate_formula(self, operator, *args):

        if operator == '||':
            return pdlsl.Or(*args)
        elif operator == '&':
            return pdlsl.And(*args)
        elif operator == '->':
            return pdlsl.Implication(*args)
        elif operator == '<->':
            return pdlsl.DoubleImplication(*args)
        elif operator == '~':
            return pdlsl.Not(*args)
        else:
            raise ValueError("Erroneous operator")
    
    def calculate_action(self, operator, *args):

        if operator == '//':
            return pdlsl.Concurrence(*args)
        elif operator == '^':
            return pdlsl.Union(*args)
        elif operator == ';':
            return pdlsl.Concatenation(*args)
        elif operator == '?':
            return pdlsl.Test(*args)
        elif operator == '**':
            return pdlsl.TransitiveClosure(*args)
        else:
            raise ValueError("Erroneous operator")
    
    def substitute_atoms(self, input_string):
        substituted = input_string
 
        atoms = self.atom_index
        actions = self.action_index
         
        for atom in atoms:
            substituted = substituted.replace(atom, "ATOM%d" % \
                                              atoms.index(atom))
        for action in actions:
            substituted = substituted.replace(action, "ACTION%d" % \
                                              actions.index(action))
             
        for articulator in self.articulators:
            substituted = substituted.replace(articulator, "ART%d" % \
                                              self.articulators.index(articulator))
        return substituted
    
    def get_articulator_atom(self, articulator_id):
        entry = int(articulator_id.replace("ART",""))
        art_name = self.articulators[entry]
        return self.atoms[art_name]
    
    def get_articulator_atomaction(self, articulator_id):
        entry = int(articulator_id.replace("ART",""))
        art_name = self.articulators[entry]
        return self.actions[art_name]