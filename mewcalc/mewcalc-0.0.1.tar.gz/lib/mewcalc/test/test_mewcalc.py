#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import unittest
from lib.mewcalc.mewcalc import MewCalc

from datetime import datetime, date, time


class MewCalcTest(unittest.TestCase):
    def setUp(self):
        self.mc = MewCalc()

    def test_human_age(self):
        """
        人間の年
        """
        born = date(1984, 1, 4)
        res = self.mc.calculate_human_age(born)
        self.assertEqual(res, 30)

    def test_cat_age(self):
        """
        猫の年
        """
        born = date(1984, 1, 4)
        res = self.mc.calculate(born)
        self.assertEqual(res, 30)

    def test_cat_year_age1(self):
        """
        2年は24歳
        """
        year = 2
        res = self.mc.calculate_by_year(year)
        self.assertEqual(res, 24)

    def test_cat_year_age2(self):
        """
        3年は28歳
        """
        year = 3
        res = self.mc.calculate_by_year(year)
        self.assertEqual(res, 24)

    def test_cat_year_age3(self):
        """
        19年は92歳
        """
        year = 19
        res = self.mc.calculate_by_year(year)
        self.assertEqual(res, 92)


if __name__ == '__main__':
    unittest.main()
