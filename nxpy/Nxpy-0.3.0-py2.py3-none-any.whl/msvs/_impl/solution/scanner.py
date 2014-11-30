# nxpy.msvs._impl.solution package -------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

from __future__ import absolute_import

import logging

import nxpy.ply.scanner

import nxpy.core._impl.log


_log = logging.getLogger(__name__)


class Scanner(nxpy.ply.scanner.Scanner):
    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(args, kwargs)

    reserved = ( 
        'Analysis',
        'Any',
        'Code',
        'CPU',
        'Debug',
        'Description',
        'EndGlobal',
        'EndGlobalSection',
        'EndProject',
        'EndProjectSection',
        'File', 
        'Format',
        'Global',
        'GlobalSection',
        'Microsoft',
        'Project',
        'ProjectSection',
        'Release',
        'Studio', 
        'Solution', 
        'Version', 
        'Visual', 
        'with',
        )
    
    tokens = [ r.upper() for r in reserved ] + [
         'COMMA',
         'EQUALS',
         'LBRACE',
         'LPAREN',
         'POINT',
         'RBRACE',
         'RPAREN',
         'VBAR',
         
         'NUMBER',
         'IDENTIFIER',
         'STRING',
         'UUID',
         ]

    # Punctuation

    t_COMMA     = r','
    t_EQUALS    = r'='
    t_LBRACE    = r'\{'
    t_LPAREN    = r'\('
    t_POINT     = r'\.'
    t_RBRACE    = r'\}'
    t_RPAREN    = r'\)'
    t_VBAR      = r'\|'
    
    t_NUMBER    = r'\d+(?:\.\d+)?'
    
    def t_STRING(self, t):
        r'\"[^\"]*\"'
        t.value = t.value[1:-1]
        return t

    def t_UUID(self, t):
        r'\w{8}(?:-\w{4}){3}-\w{12}'
        return t
    
    _reserved_map = dict([ ( s, s.upper() ) for s in reserved ])

    def t_DESCRIPTION(self, t):
        r'Description[ \t]*=[^\n]*'
        t.value = ( t.value, t.lexer.lexpos )
        return t
    
    def t_IDENTIFIER(self, t):
        r'[A-Za-z_][\w_]*'
        t.type = self._reserved_map.get(t.value,"IDENTIFIER")
        t.value = ( t.value, t.lexer.lexpos )
        return t

    # Whitespace
    
    t_ignore = ' \t'
    
    # Comments

    def t_comment(self, t):
        r'\#.*[\n\r]+'
        t.lineno += t.value.count('\n')

    # Line counter

    def t_newline(self, t):
        r'[\n\r]+'
        t.lineno += t.value.count("\n")

    # Errors

    def t_error(self, t):
        _log.error("Illegal character: '%s'", t.value[0])
        t.lexer.skip(1)
