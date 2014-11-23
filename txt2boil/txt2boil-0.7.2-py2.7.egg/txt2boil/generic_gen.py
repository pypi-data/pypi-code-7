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

"""This module provides a universal generic generator.

The GenericGen encompasses all the generic generators available by
inheiriting from each and every one of them.  This makes it easy for
people to add languages because they can just have their class inherit
from this one so that their language will support all the available
features.

"""


# To add additional generators, just add an import statement that
# exposes the generator to the module level namespace.  The GenericGen
# class will pick it up automatically and generate the appropriate
# code for it.

# from .core import Gen
from .linegen import LineCodeGen
from .pygen import PyGen


def collectGenerators(cls):
    if isinstance(cls, str):
        cls = globals()[cls]
    klasses = [c for (nm, c) in globals().items() if nm.endswith('Gen')]
    parents = tuple(klasses)
    return type(cls.__name__, parents, dict(cls.__dict__))


# GenericGen will inherit from any class in module level scope that
# ends with the name Gen.
@collectGenerators
class GenericGen(object):

    """A generic generator.

    This includes the functionally of all language agnostic generators
    and as such can be used as the main parent class when defining a
    new language class.

    It also provides an easy way to add language agnostic generators
    to all the languages without editing each class file.  You simply
    add an import statement to the top of this module and GenericGen
    will take care of everything else.

    """

    pass


__all__ = ['GenericGen']
