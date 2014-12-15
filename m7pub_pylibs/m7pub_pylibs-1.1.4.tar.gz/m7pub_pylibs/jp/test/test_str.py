#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the jp.str module
"""

__author__      = "Iqbal Abdullah <iqbal@marimore.co.jp>"
__date__        = "$LastChangedDate: 2011-01-12 19:45:45 +0900 (Wed, 12 Jan 2011) $"
__version__     = "$LastChangedRevision: 151 $"

import sys
import os
import unittest

file_path = os.path.abspath(__file__)
parent_directory = "/".join(file_path.split('/')[:-2])
sys.path.insert(0, parent_directory)

from str import is_only_fullwidth_katakana

class TestStrModule(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_fullwidth_katakana_only(self):

        s = "アイウエオカキクケコサシスセソナニヌネノタツヅテトパピプペポ".decode('utf-8')
        self.assertTrue(is_only_fullwidth_katakana(s))

        s = "ッゥォポヲュヮ".decode('utf-8')
        self.assertTrue(is_only_fullwidth_katakana(s))

        s = "デンワカケルサービス".decode('utf-8')
        self.assertTrue(is_only_fullwidth_katakana(s))

    def test_ascii(self):

        s = "ab4gty?".decode('utf-8')
        self.assertFalse(is_only_fullwidth_katakana(s))

    def test_hiragana_only(self):

        s = "あいうえお".decode('utf-8')
        self.assertFalse(is_only_fullwidth_katakana(s))

    def test_halfwidth_katakana_only(self):

        s = "ｶﾀｶﾅﾎﾟﾋﾟﾌﾟｩｫｯ".decode('utf-8')
        self.assertFalse(is_only_fullwidth_katakana(s))

    def test_mixed_katakana_and_hiragana(self):

        s = "カキかきコこ".decode('utf-8')
        self.assertFalse(is_only_fullwidth_katakana(s))


if __name__ == '__main__':
    unittest.main()

