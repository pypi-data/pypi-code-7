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

from .core import *
import re


class Comments(Extractor):

    """A base class to identify subclasses as being comment classes.

    """

    pass


class Shell(Comments):

    """Handle shell style comments.

    """

    __regex = re.compile(r'^#+ (.*\n)', re.M)

    def lineComment(self, text, start):
        return self.__regex.search(text, start)


class Lisp(Comments):

    """Handle lisp style comments.

    """

    __regex = re.compile(r'^;+ (.*\n)', re.M)

    def lineComment(self, text, start):
        return self.__regex.search(text, start)


class C(Comments):

    """Handle C style /* ... */ comments.

    """

    __regex = re.compile(r'/\* (.*?)\*/', re.M | re.S)

    def blockComment(self, text, start):
        return self.__regex.search(text, start)


class CXX(C):

    """Handle C++ style // ... comments.

    """

    __regex = re.compile(r'^//+ (.*\n)', re.M)

    def lineComment(self, text, start):
        return self.__regex.search(text, start)


class TeX(Comments):

    """The comment style used in dialects of TeX."""

    __regex = re.compile(r'^%+ (.*\n)', re.M)

    def lineComment(self, text, start):
        return self.__regex.search(text, start)
