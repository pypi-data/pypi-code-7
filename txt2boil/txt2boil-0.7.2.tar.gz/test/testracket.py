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

from .testgen import TestGen
from txt2boil.langs import Racket


class RacketConstantTester(TestGen, Racket):

    """Test the boilerplate generation in Racket code.

    """

    basicText = r"""
;; Constant Gen: r(\d+)/(\d+) (make-my-rational \1 \2)

r5/7
"""

    basicAnswer = r"""
;; Constant Gen: r(\d+)/(\d+) (make-my-rational \1 \2)
(define r5/7 (make-my-rational 5 7))

r5/7
"""

    blahComment = r"""
;; blah
"""

    def test_solecomment(self):
        """Test the constant generation.

        """

        self.checkGenerates(self.basicText, self.basicAnswer)

    def test_onecommentwithothers(self):
        """Test with the existence of other comments.

        """

        self.checkGenerates(self.blahComment + self.basicText,
                            self.blahComment + self.basicAnswer)

    def test_extractmany(self):
        """Test the extraction of many comments.

        """

        c = self.comments(r"""
;; foo

;; bar
""")
        self.assertEqual(c, ['foo\n', 'bar\n'])

    def test_commentextraction(self):
        """Test the extraction of comments.

        """

        c = self.comments(self.basicAnswer)
        self.assertEqual(
            c, [r"Constant Gen: r(\d+)/(\d+) (make-my-rational \1 \2)" +
                "\n"])

    lineGenTest = r"""
;; Line Gen:
;; r(\d+)/(\d+)
;; (define \g<0> (make-my-rational \1 \2))

r5/7
"""

    lineGenAnswer = r"""
;; Line Gen:
;; r(\d+)/(\d+)
;; (define \g<0> (make-my-rational \1 \2))
(define r5/7 (make-my-rational 5 7))

r5/7
"""

    def testLineGen(self):
        self.checkGenerates(self.lineGenTest, self.lineGenAnswer)
