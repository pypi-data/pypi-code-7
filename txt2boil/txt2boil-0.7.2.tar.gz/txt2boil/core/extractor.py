#!/usr/bin/python

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


"""An extractor class that extracts the content from comments.

"""

from itertools import groupby
import re


class Extractor(object):

    """A class that extracts the comments from source code text.

    """

    _emptylineregex = re.compile('^()$^$', re.M)

    def lineComment(self, text, start):
        """Return a match object for a line comment in text starting at start.

        Overload this method to control what comments are matched.

        """

        pass

    def blockComment(self, text, start):
        """Return a match object for a block comment in text starting at
        start.

        Overload this method to control how block comments are
        matched.

        """

        pass

    def nextComment(self, text, start=0):
        """Return the next comment found in text starting at start.

        """

        m = min([self.lineComment(text, start),
                 self.blockComment(text, start),
                 self._emptylineregex.search(text, start)],
                key=lambda m: m.start(0) if m else len(text))
        return m

    def hasLineComment(self, text):
        """Return true if text contains a line comment.

        """

        return self.lineComment(text, 0) is not None

    def isLineComment(self, text):
        """Return true if the text is a line comment.

        """

        m = self.lineComment(text, 0)
        return m and m.start(0) == 0 and m.end(0) == len(text)

    def nextValidComment(self, text, start=0):
        """Return the next actual comment.

        """

        m = min([self.lineComment(text, start),
                 self.blockComment(text, start)],
                key=lambda m: m.start(0) if m else len(text))
        return m

    def extractContent(self, text):
        """Extract the content of comment text.

        """

        m = self.nextValidComment(text)
        return '' if m is None else m.group(1)

    def extractChunkContent(self, lst):
        """Extract the content of a chunk (a list of comments) and represent
        that as a single string.

        """

        return ''.join(map(self.extractContent, lst))

    def chunkComment(self, text, start=0):
        """Return a list of chunks of comments.

        """

        # Build a list of comments
        comm, out = self.nextComment(text, start), []
        while comm:
            out.append(comm.group(0))
            comm = self.nextComment(text, comm.start(0) + 1)

        # Collect the comments according to whether they are line
        # comments or block comments.
        out = [list(g) for (_, g) in groupby(out, self.isLineComment)]

        # Filter out seperator lines.
        out = [i for i in out if i != ['']]

        return out

    def comments(self, text, start=0):
        """Return a list of comments.

        """

        out = [self.extractChunkContent(s)
               for s in self.chunkComment(text, start)]
        return out

    def code(self, text):
        """Return the code instead of the comments.

        """

        comm = self.nextValidComment(text)
        while comm:
            text = text[:comm.start()] + text[comm.end():]
            comm = self.nextValidComment(text, comm.end(0))
        return text
