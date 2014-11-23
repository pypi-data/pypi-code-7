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

from testgen import TestGen
from langs import Python


class PythonTester(Python, TestGen):

    basicTest = r"""
# Line Gen:
# g(\d+)_(\d+)
# \g<0> = divmod(\1, \2)

print g9_7
"""

    basicAnswer = r"""
# Line Gen:
# g(\d+)_(\d+)
# \g<0> = divmod(\1, \2)
g9_7 = divmod(9, 7)

print g9_7
"""

    def testBasic(self):
        self.checkGenerates(self.basicTest, self.basicAnswer)
