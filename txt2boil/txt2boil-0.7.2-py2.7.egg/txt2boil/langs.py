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

"""Frontend interface to the txt2boil library.

Each class is designed for a particular language and inherits its
features from different parent classes.

A language class is defined to be a class in the global scope of this
module and has a class level ext field.  The ext field must be a list
of file name extensions.  Thus, all language classes will be exported
by this module and registered in the __all__ list.  So to import all
languages it is safe to use::

    from langs import *

"""


from . import cmi
from .core import HookedRegex
from .generic_gen import GenericGen
from . import comments
import collections


class Unknown(GenericGen):

    """The default "unknown" language."""

    pass


class Python(comments.Shell, GenericGen):

    """The Python language."""

    ext = ['.py']


class _RacketConstantGen(GenericGen):

    """Auto generate constants for Racket code.

    """

    @cmi.nonNoneCMI(lambda: _RacketConstantGen)
    def matchComment(self, comm):
        return HookedRegex(r'Constant Gen: (\S+) (.*)\n',
                           '(define \g<0> {})\n', comm)


class Racket(_RacketConstantGen, comments.Lisp, GenericGen):

    """The Racket language.

    Racket was the language that originally inspired this project as
    it was the language of choice for my university professors.

    """

    ext = ['.rkt']


class C(comments.C, GenericGen):

    """The C language, without the // line comments."""

    ext = '.c .h'.split()


class CXX(comments.CXX, GenericGen):

    """The C++ language, including both block and line comments."""

    ext = '.cc .cpp .hh .hpp'.split()


class Java(CXX):

    """Oracle's Java programming language.

    It currently extends the C++ language as there are no
    specializations for it yet.

    """

    ext = ['.java']


class LaTeX(comments.TeX, GenericGen):

    """The LaTeX typesetting language."""

    ext = '.tex .sty .cls'.split()


# Export all the classes with an ext field in them.  This is how we
# denote language classes from all other kinds of classes.
__all__ = sorted([nm for (nm, cls) in globals().items()
                  if hasattr(cls, 'ext')])
