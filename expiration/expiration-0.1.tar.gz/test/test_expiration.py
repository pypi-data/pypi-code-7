#######################################################################
# Tests for expiration module.
#
# Copyright 2014 True Blade Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Notes:
########################################################################

from expiration import find_expired_items, RetentionCriterion, RetentionRules, date

import sys
import unittest
from datetime import timedelta, datetime
from operator import attrgetter
from collections import namedtuple

_PY2 = sys.version_info[0] == 2
_PY3 = sys.version_info[0] == 3

# we'll use this item for testing
Item = namedtuple('Item', 'name expires')
getter = attrgetter('expires')

class TestExpiration(unittest.TestCase):
    def test_types(self):
        # just test that we can create our various types
        rules = RetentionRules(None, [])
        rules = RetentionRules(timedelta(days=1), [RetentionCriterion(1, date.day_of),
                                                   RetentionCriterion(2, date.week_of),
                                                   RetentionCriterion(3, date.month_of),
                                                   RetentionCriterion(4, date.quarter_of),
                                                   RetentionCriterion(5, date.year_of),
                                                   ])

    def test_no_rules(self):
        items = [Item(1, datetime(1900, 1, 1)),
                 Item(2, datetime(2014, 3, 3)),
                 ]

        rules = RetentionRules(None, [])
        self.assertEqual(list(find_expired_items(items, getter, rules, asof_timestamp=datetime(2100, 1, 1))), [])

        rules = RetentionRules(timedelta(days=1000), [])
        self.assertEqual(list(find_expired_items(items, getter, rules, asof_timestamp=datetime(2100, 1, 1))), [(items[0], None),
                                                                                                               (items[1], None),
                                                                                                               ])



class TestAll(unittest.TestCase):
    def test_all(self):
        import expiration

        # check that __all__ in the module contains everything that should be
        #  public, and only those symbols
        all = set(expiration.__all__)

        # check that things in __all__ only appear once
        self.assertEqual(len(all), len(expiration.__all__),
                         'some symbols appear more than once in __all__')

        # get the list of public symbols
        found = set(name for name in dir(expiration) if not name.startswith('_'))

        # make sure it matches __all__
        self.assertEqual(all, found)


unittest.main()
