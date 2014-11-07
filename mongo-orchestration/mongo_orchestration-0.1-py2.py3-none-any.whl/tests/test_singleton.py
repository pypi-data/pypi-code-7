#!/usr/bin/python
# coding=utf-8
# Copyright 2012-2014 MongoDB, Inc.
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

import sys

sys.path.insert(0, '../')

from mongo_orchestration.singleton import Singleton
from nose.plugins.attrib import attr
from tests import unittest


@attr('singleton')
@attr('test')
class SingletonTestCase(unittest.TestCase):

    def test_singleton(self):
        a = Singleton()
        b = Singleton()
        self.assertEqual(id(a), id(b))
        c = Singleton()
        self.assertEqual(id(c), id(b))


if __name__ == '__main__':
    unittest.main()
