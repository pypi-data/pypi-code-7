# nxpy.msvs._impl.solution package -------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

from __future__ import absolute_import

import re


class Description(object):
    descRe = re.compile('Description[ \t]*=(.*)')
    
    def __init__(self, value):
        self.len = len(value[0])
        self.pos = value[1] - self.len
        m = self.descRe.match(value[0])
        if m and m.groups is not None:
            self.value = m.group(1).strip()
        else:
            self.value = ""


class Project(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __str__(self):
        return " ".join([ "Project:", self.name, "-", self.path ]) 


class Solution(object):
    def __init__(self, text, version, projects, description):
        self.text = text
        self.version = version
        self.projects = projects
        self.description = description
        
    def __str__(self):
        return "\n\t".join([ "Solution " + self.version, ] + [ str(p) for p in self.projects ])
