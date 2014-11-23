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

"""Cooprative Multiple Inheritance (CMI) made easy.

This module provides a function descriptor that transforms an ordinary
overloaded function into a function that is compatible with CMI.  This
allows us to mimic the Chain of Resposibility design pattern entirely
using CMI.

There are two API's.  One is the generic descripter that takes a
binary operation and uses it to merge two answers together.  The other
is two functions: one which locates the first non-None object and
returns it, and the other which finds the minimum element of all the
posibilities.

Note that all the cls arguments to the descriptors must be passed
wrapped in a lambda like so:

class Foo:
    @nonNoneCMI(lambda: Foo)
    def bar(self):
        pass

Otherwise the name Foo won't be defined yet.

"""

from functools import wraps


class AbstractCMI:

    """A descriptor that enables easy CMI according to a function.

    The final result function will be achieved by using merge as a
    binary operation on the results of the current function and the
    super-class' function of the same name.

    """

    def __init__(self, cls, merge):
        """Initialize the abstract descriptor.

        Note that cls has to be wrapped in a lambda because otherwise
        there will be a name resolution error (since that class hasn't
        been defined yet).

        cls   - the current class wrapped in a lambda
        merge - the binary operator that will determine the final
                result

        """

        self.cls = cls
        self.merge = merge

    def _getSuperFunc(self, s, func):
        """Return the the super function."""

        return getattr(super(self.cls(), s), func.__name__)

    def __call__(self, func):
        """Apply this abstract descriptor to func."""

        @wraps(func)
        def wrapper(s, *args, **kwargs):
            a = func(s, *args, **kwargs)
            b = self._getSuperFunc(s, func)(*args, **kwargs)
            return self.merge(a, b)
        return wrapper


def minCMI(cls):
    """Return an AbstractCMI that locates the minimum element."""

    return AbstractCMI(cls, min)


def nonNoneCMI(cls):
    """Return an AbstractCMI that locates the first non-None element."""

    return AbstractCMI(cls, lambda x, y: x if x is not None else y)

__all__ = ['AbstractCMI', 'minCMI', 'nonNoneCMI']
