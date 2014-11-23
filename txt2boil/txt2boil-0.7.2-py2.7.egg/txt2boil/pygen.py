# Copyright (C) 2014 Kieran Colford
#
# This file is part of txt2boil.
#
# txt2boil is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# txt2boil is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with txt2boil.  If not, see <http://www.gnu.org/licenses/>.

"""A generator that uses python code to generate its output.

"""

import textwrap
from .core import *
from . import cmi


class _PyGenHookedRegex(HookedRegex):

    """A special object that returns the regex r'^.*$' for the trigger.

    """

    def group(self, n=0):
        if n == 0:
            return super(_PyGenHookedRegex, self).group(n)
        elif n == 1:
            return r'(?s)^(.*)$'
        else:
            return super(_PyGenHookedRegex, self).group(n - 1)

    def output(self, match):
        code = 'def foo(env):\n' + self.group(2)
        code = code.splitlines()
        code = '\n    '.join(code)
        env = {}
        eval(code, env)
        return env['foo'](match.group(0))


class PyGen(Gen):

    """Generate output code using the python code provided in a comment.

    The code is treated as the body of a function who's argument is
    env.  This function is provided with the full text of the source
    file (with comments stripped) inside of env and is expected to
    return a string of the code to be inserted.  For example::

        # Python Gen:
        # if env.startswith('#!'):
        #     return 'I am in a unix script'
        # else:
        #     return 'I am an ordinary module'

        ...

    Would then become:

        # Python Gen:
        # if env.startswith('#!'):
        #     return 'I am in a unix script'
        # else:
        #     return 'I am an ordinary module'
        I am an ordinary module

        ...

    Note that even though there was no newline at the end of the
    string, one as added anyways.

    """

    @cmi.nonNoneCMI(lambda: PyGen)
    def matchComment(self, comm):
        return _PyGenHookedRegex(r'(?s)Python Gen:\n(.*)', '', comm)
