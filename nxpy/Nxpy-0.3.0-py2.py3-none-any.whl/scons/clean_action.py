# nxpy.scons package ---------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
SCons Actions to be performed when cleaning.

"""

from __future__ import absolute_import

import nxpy.scons.util


def clean_action(env, targets, action):
    r"""
    To be installed with:
    env.AddMethod(nxpy.scons.clean_action.clean_action, 'CleanAction')
    """
    if nxpy.scons.util.is_cleaning(env, targets):
            env.Execute(action)
