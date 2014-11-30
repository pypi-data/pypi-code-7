# nxpy.scons package ---------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Utilities for the SCons build tool.

"""

from __future__ import absolute_import

import os

from six.moves import range


# Taken almost verbatim from this SCons Wiki recipe: http://www.scons.org/wiki/CustomCleanActions
# (If you are the original author and object to this being here, get in touch!)
 
def is_cleaning(env, targets):
        if not env.GetOption('clean'):
                return False
        # normalize targets to absolute paths
        targets = env.subst('${TARGETS.abspath}', target=targets).split()
        launchdir = env.GetLaunchDir()
        topdir = env.Dir("#").abspath
        cl_targets = env.subst('$COMMAND_LINE_TARGETS').split()
        if len(cl_targets) == 0:
                cl_targets.append(".")
        for i in range(len(cl_targets)):
                full_target = ""
                if cl_targets[i][0] == '#':
                        full_target = os.path.join(topdir,cl_targets[i][1:0])
                else:
                        full_target = os.path.join(launchdir,cl_targets[i])
                full_target = os.path.normpath(full_target)
                for target in targets:
                        if target.startswith(full_target):
                                return True
        return False
