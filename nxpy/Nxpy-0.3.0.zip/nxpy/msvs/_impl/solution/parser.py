# nxpy.msvs._impl.solution package -------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

from __future__ import absolute_import

import logging

import nxpy.ply.parser

import nxpy.core._impl.log
import nxpy.msvs._impl.solution.ast


_log = logging.getLogger(__name__)


class Parser(nxpy.ply.parser.Parser):
    def __init__(self, *args, **kwargs):
        super(Parser, self).__init__(*args, **kwargs)
        self.desc_pos = -1

    def p_solution(self, t):
        r'solution : version projects global'
        desc = t[3]
        if desc is None:
            desc = nxpy.msvs._impl.solution.ast.Description(("", self.desc_pos))
        t[0] = nxpy.msvs._impl.solution.ast.Solution(self.text, t[1], t[2], desc)
    
    def p_version(self, t):
        r'version : MICROSOFT VISUAL STUDIO SOLUTION FILE COMMA FORMAT VERSION NUMBER'
        t[0] = t[9]

    def p_projects(self, t):
        r'''projects : projects project 
                       | project'''
        if len(t) == 3:
            t[0] = t[1] + [ t[2] ]
        else:
            t[0] = [ t[1] ]
    
    def p_project(self, t):
        r'project : PROJECT LPAREN STRING RPAREN EQUALS project_def ENDPROJECT'
        t[0] = t[6]
    
    def p_project_def(self, t):
        r'project_def : STRING COMMA STRING COMMA STRING project_section'
        t[0] = nxpy.msvs._impl.solution.ast.Project(t[1], t[3])
    
    def p_project_section(self, t):
        r'''project_section : PROJECTSECTION tokens ENDPROJECTSECTION
                              | empty'''
        pass

    def p_global(self, t):
        r'global : GLOBAL global_sections ENDGLOBAL'
        t[0] = t[2]
    
    def p_global_sections(self, t):
        r'''global_sections : global_sections global_section
                              | global_section'''
        if t[1] is not None:
            t[0] = t[1]
        elif len(t) == 3:
            t[0] = t[2]
    
    def p_global_section(self, t):
        r'''global_section : GLOBALSECTION LPAREN IDENTIFIER RPAREN EQUALS IDENTIFIER property_list ENDGLOBALSECTION'''
        t[0] = t[7]
        if t[3][0] == "SolutionConfigurationPlatforms":
            self.desc_pos = t[8][1] - len(t[8][0]) - 1

    def p_property_list(self, t):
        r'''property_list : properties DESCRIPTION
                            | properties'''
        if len(t) == 3:
            t[0] = nxpy.msvs._impl.solution.ast.Description(t[2])
            
    def p_tokens(self, t):
        r'''tokens : anything
                     | tokens anything'''
        if len(t) == 3:
            t[0] = " ".join([ t[1], t[2] ])
        else:
            t[0] = t[1]
    
    def p_anything(self, t):
        r'''anything : COMMA
                       | EQUALS
                       | LBRACE
                       | LPAREN
                       | POINT
                       | RBRACE
                       | RPAREN
                       | VBAR
                       | NUMBER
                       | IDENTIFIER
                       | STRING
                       | UUID
                       | ANY'''
        t[0] = t[1]

    def p_properties(self, t):
        r'''properties : properties property
                         | property'''
        pass

    def p_property(self, t):
        r'''property : term EQUALS term'''
        pass
                
    def p_term(self, t):
        r'''term : build VBAR platform
                   | IDENTIFIER'''
        pass
        
    def p_build(self, t):
        r'''build : LBRACE UUID RBRACE POINT build_type
                    | build_type'''
        pass
    
    def p_build_type(self, t):
        r'''build_type : DEBUG
                         | release'''
        pass
    
    def p_platform(self, t):
        r'''platform : ANY CPU details
                       | ANY CPU'''
        pass
    
    def p_details(self, t):
        r'''details : details POINT detail
                      | POINT detail'''
        pass
    
    def p_detail(self, t):
        r'''detail : DEBUG
                     | release
                     | IDENTIFIER
                     | NUMBER'''
        pass
    
    def p_release(self, t):
        r'''release : RELEASE WITH CODE ANALYSIS
                      | RELEASE'''
        pass

    def p_empty(self, t):
        'empty :'
        pass

    def p_error(self, t):
        _log.error("Syntax error: line (" + str(t.lineno) + ") " + t.type + " = " + t.value)

    def parse(self, text):
        self.text = text
        text = text.split('\n', 1)
        return super(Parser, self).parse(text[1])
