# nxpy.scons package ---------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2012
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Support for handling project files with SCons, i.e. use it as a meta-build tool.

"""

class Project(object):
    def __init__(self):
        self.projects = {}
    
    def add(self, env, target, path):
        self.projects[str(target)] = path
        
    def __call__(self, target, source, env, for_signature):
        return self.projects[str(target)]