#!/usr/bin/env python

import sys
import unittest
import random
from __init__ import PDSAvails

TEST_API_KEY='58178a3b56814f9d'
TEST_API_PASS='73f253a65db94cd3'


class TestPDSAvails(unittest.TestCase):


    def setUp(self):
        self.avails = PDSAvails(TEST_API_KEY, TEST_API_PASS)


    def test001_validate_user(self):
        """
        Test to make sure a valid user account
        and that the status code returned is 200.
        """
        res = self.avails.validate_credentials()
        self.assertEquals(res['StatusCode'], 200)


if __name__ == "__main__":
    unittest.main()




