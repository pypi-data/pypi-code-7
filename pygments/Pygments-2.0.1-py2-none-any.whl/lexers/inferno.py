# -*- coding: utf-8 -*-
"""
    pygments.lexers.inferno
    ~~~~~~~~~~~~~~~~~~~~~~~

    Lexers for Inferno os and all the related stuff.

    :copyright: Copyright 2006-2014 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, include, bygroups, default
from pygments.token import Punctuation, Text, Comment, Operator, Keyword, \
    Name, String, Number

__all__ = ['LimboLexer']


class LimboLexer(RegexLexer):
    """
    Lexer for `Limbo programming language <http://www.vitanuova.com/inferno/limbo.html>`_

    TODO:
        - maybe implement better var declaration highlighting
        - some simple syntax error highlighting

    .. versionadded:: 2.0
    """
    name = 'Limbo'
    aliases = ['limbo']
    filenames = ['*.b']
    mimetypes = ['text/limbo']

    tokens = {
        'whitespace': [
            (r'^(\s*)([a-zA-Z_]\w*:(\s*)\n)',
             bygroups(Text, Name.Label)),
            (r'\n', Text),
            (r'\s+', Text),
            (r'#(\n|(.|\n)*?[^\\]\n)', Comment.Single),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|'
             r'u[a-fA-F0-9]{4}|U[a-fA-F0-9]{8}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String), # all other characters
            (r'\\', String), # stray backslash
        ],
        'statements': [
            (r'"', String, 'string'),
            (r"'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", String.Char),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])', Number.Float),
            (r'16r[0-9a-fA-F]+', Number.Hex),
            (r'8r[0-7]+', Number.Oct),
            (r'((([1-3]\d)|([2-9]))r)?(\d+)', Number.Integer),
            (r'[()\[\],.]', Punctuation),
            (r'[~!%^&*+=|?:<>/-]|(->)|(<-)|(=>)|(::)', Operator),
            (r'(alt|break|case|continue|cyclic|do|else|exit'
             r'for|hd|if|implement|import|include|len|load|or'
             r'pick|return|spawn|tagof|tl|to|while)\b', Keyword),
            (r'(byte|int|big|real|string|array|chan|list|adt'
             r'|fn|ref|of|module|self|type)\b', Keyword.Type),
            (r'(con|iota|nil)\b', Keyword.Constant),
            ('[a-zA-Z_]\w*', Name),
        ],
        'statement' : [
            include('whitespace'),
            include('statements'),
            ('[{}]', Punctuation),
            (';', Punctuation, '#pop'),
        ],
        'root': [
            include('whitespace'),
            default('statement'),
        ],
    }

    def analyse_text(text):
        # Any limbo module implements something
        if re.search(r'^implement \w+;', text, re.MULTILINE):
            return 0.7

# TODO:
#   - Make lexers for:
#       - asm sources
#       - man pages
#       - mkfiles
#       - module definitions
#       - namespace definitions
#       - shell scripts
#       - maybe keyfiles and fonts
#   they all seem to be quite similar to their equivalents
#   from unix world, so there should not be a lot of problems
