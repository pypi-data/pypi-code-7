# nxpy.msvs package ----------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Manipulation of Microsoft Visual Studio solution files.

Currently supports Visual Studio 2008 (9.0) only.

Requires at least Python 2.6 and `ply <https://pypi.python.org/pypi/ply>`_.

"""

# Alllows for more gracious failure on Python 2.5
from __future__ import with_statement
from __future__ import absolute_import

import os.path

import six

import nxpy.core.file

import nxpy.msvs._impl.solution.parser
import nxpy.msvs._impl.solution.scanner


class Description(object):
    def __init__(self, ast, disp):
        self.pos = ast.pos + disp
        self.len = ast.len
        self._value = ast.value
        self.modified = False
        
    def _get_value(self):
        return self._value
    def _set_value(self, value):
        if value != self._value:
            self._value = value
            self.modified = True
    value = property(_get_value, _set_value)

    def update(self, text):
        if len(self.value) != 0:
            t = [ text[:self.pos] ]
            if self.len == 0:
                t.append("\t")
            v = "Description = " + self.value
            t.append(v)
            if self.len == 0:
                t.append("\n")
            t.append(text[self.pos+self.len:])
            self.len = len(v)
            return "".join(t)
        else:
            t = [ text[:self.pos].rstrip() ]
            t.append(text[self.pos+self.len].lstrip(" \t"))
            self.pos = len(t[0])
            self.len = 0
            return "".join(t)
        
            
class Solution(object):
    def __init__(self, path):
        self.path = os.path.realpath(path)
        self.dir, self.file = os.path.split(self.path)
        self.name = os.path.splitext(self.file)[0]
        ast = self._read(debug=1)
        self.text = ast.text
        self.version = ast.version
        self._description = Description(ast.description, len(self.text.splitlines(True)[0]))
        self.projects = {}
        for p in ast.projects:
#            l = [ self.dir, ]
#            l.extend(p.path.split("\\"))
#            self.projects[p.name] = os.path.join(*l)
            self.projects[p.name] = os.path.join(self.dir, p.path)

    def _read(self, debug=False):
        scanner = nxpy.msvs._impl.solution.scanner.Scanner(debug=debug)
        parser = nxpy.msvs._impl.solution.parser.Parser(scanner, debug=debug)
        with nxpy.core.file.open_(self.path, "r", encoding="utf-8") as f:
            return parser.parse(f.read())

    def _get_description(self):
        return self._description.value
    def _set_description(self, value):
        self._description.value = value
    description = property(_get_description, _set_description)

    def write(self, where):
        if not where:
            where = self.path            
        if isinstance(where, six.string_types):
            f = nxpy.core.file.open_(where, "w+", encoding="utf-8")
        else:
            f = where
        try:
            t = self._description.update(self.text)
            if t is None:
                t = self.text
            f.write(t)
            self.text = t
        finally:
            f.close()
        
    def save(self):
        if self._description.modified:
            self.write(None)
            return True
        return False

    def __str__(self):
        return "\n\n".join([ " ".join([ "Solution", self.name, self.version, self.dir ]) ] + 
                            [ str(p) for p in self.projects.values() ])
