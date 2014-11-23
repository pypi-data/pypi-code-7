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

"""A regex match object with a hook for generating output.

"""

import re


class HookedRegex(object):

    """A regex object with a hook that generates output from what it has
    matched.

    """

    def __new__(cls, match, template, text):
        if re.match(match, text, re.M) is None:
            return None
        return super(HookedRegex, cls).__new__(cls)

    def __init__(self, match, template, text):
        """Initialize the object as a clone of another regex, but add a hook
        to it this time.

        """

        self.regex = re.match(match, text, re.M)
        self.template = template

    def __bool__(self):
        return self.regex is not None

    def group(self, n=0):
        return self.regex.group(n)

    @property
    def match(self):
        """The regex string that this regex will be triggered by."""

        return self.group(1)

    @property
    def text(self):
        """The text that this regex was instantiated by."""

        return self.group(0)

    def output(self, match):
        return match.expand(self.template.format(self.regex.group(2)))
