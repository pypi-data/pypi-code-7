"""Unit tests for basic IRC message formatting."""
# pylint: disable=missing-docstring,too-few-public-methods


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import unittest

from ..formatters import line_as_html


IRC_AS_HTML = [
    ('regular', 'regular'),
    ('\x02bold', '<span style="font-weight: bold">bold</span>'),
    ('\x02bold\x0F', '<span style="font-weight: bold">bold</span>'),
    ('\x02bold\x02reg', '<span style="font-weight: bold">bold</span>reg'),
    ('\x031colorized', '<span style="color: black">colorized</span>'),
    ('\x031,1colorized',
     '<span style="background-color: black; color: black">colorized</span>'),
    ('\x031,1colorized\x02plus bold',
     '<span style="background-color: black; color: black">colorized</span>'
     '<span style="background-color: black; color: black; '
     'font-weight: bold">plus bold</span>'),
]


class TemplateTagsTestCase(unittest.TestCase):
    def test_ircformat(self):
        for irc, html in IRC_AS_HTML:
            self.assertEqual(line_as_html(irc), html)
