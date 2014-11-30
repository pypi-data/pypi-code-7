# nxpy.scons package ---------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Microsoft Visual Studio configuration.

"""

from __future__ import absolute_import

import SCons.Builder

import nxpy.scons.clean_action
import nxpy.scons.project


def _clean_project(env, target):
    env.CleanAction(target, SCons.Action(env.subst('msbuild "$PROJECT" /t:Clean', 
            target=target)))

    
def environment(version=None, 
        script='C:/Program Files (x86)/Microsoft Visual Studio 9.0/Common7/Tools/vsvars32.bat'):
    bldr = SCons.Builder(action = 'msbuild "$PROJECT"')
    proj = nxpy.scons.project.Project()
    kwargs = { 'BUILDERS' : {'Assembly' : bldr}, 'PROJECT' : proj }
    if version:
        kwargs['MSVC_VERSION'] = version
    elif script:
        kwargs['MSVC_USE_SCRIPT'] = script
    env = SCons.Environment(**kwargs)
    env.AddMethod(nxpy.scons.clean_action.clean_action, 'CleanAction')
    env.AddMethod(proj.add, 'AddProject')
    env.AddMethod(_clean_project, 'CleanProject')
    return env
