#!/usr/bin/env python
"""This tests the Wix Instance functions to ensure that everything works
as expected.
"""

from sys import version_info
from unittest import TestCase, main
import wixinstance


class InstanceTestCase(TestCase):
    """Sets up the Wix secret and various instances.

    The secret and some are the instances are from real Wix apps. Obviously,
    these are just test apps that are not in production.

    For the fake instances based on the real instances, a single character from
    the first part (before the dot) of the real instances was changed.
    """
    def setUp(self):
        if version_info[0] >= 3:
            self.result_type = str
        else:
            self.result_type = unicode
        self.secret = "69ce77e6-2ac1-42ee-bf80-736ef3218c9d"
        self.real_instance_from_owner = "ZqQSCUe4Kk6z2EhAbakUNAifGtSTnrogcxySPwz9EM0.eyJpbnN0YW5jZUlkIjoiMTM4ZGVmZDgtNWU0Ni1hNDgyLTk0OGItMTJiMzdjNjZiYmFmIiwic2lnbkRhdGUiOiIyMDE0LTA4LTI2VDA0OjM5OjMxLjAxMC0wNTowMCIsInVpZCI6IjU0NjgzNWU1LWYyMzQtNDg3NC05NGQxLTcyMmJhZDI2YzY4OSIsInBlcm1pc3Npb25zIjoiT1dORVIiLCJpcEFuZFBvcnQiOiIxMDguMjI1LjE4OS4xNy82MzM0NiIsInZlbmRvclByb2R1Y3RJZCI6bnVsbCwiZGVtb01vZGUiOmZhbHNlfQ"
        self.real_instance_from_visitor = "dF6lBbHgD6AH8BGJLuJ2Pb4jgAOlBG7xC7EP-kPzqMA.eyJpbnN0YW5jZUlkIjoiMTM4ZGVmZDgtNWU0Ni1hNDgyLTk0OGItMTJiMzdjNjZiYmFmIiwic2lnbkRhdGUiOiIyMDE0LTA4LTI2VDA0OjQ4OjE1Ljc2Ni0wNTowMCIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlwQW5kUG9ydCI6IjEwOC4yMjUuMTg5LjE3LzY0MDU3IiwidmVuZG9yUHJvZHVjdElkIjpudWxsLCJkZW1vTW9kZSI6ZmFsc2V9"
        self.fake_instance_based_on_real_instance_owner = "ZqQSCUe4Kk7z2EhAbakUNAifGtSTnrogcxySPwz9EM0.eyJpbnN0YW5jZUlkIjoiMTM4ZGVmZDgtNWU0Ni1hNDgyLTk0OGItMTJiMzdjNjZiYmFmIiwic2lnbkRhdGUiOiIyMDE0LTA4LTI2VDA0OjM5OjMxLjAxMC0wNTowMCIsInVpZCI6IjU0NjgzNWU1LWYyMzQtNDg3NC05NGQxLTcyMmJhZDI2YzY4OSIsInBlcm1pc3Npb25zIjoiT1dORVIiLCJpcEFuZFBvcnQiOiIxMDguMjI1LjE4OS4xNy82MzM0NiIsInZlbmRvclByb2R1Y3RJZCI6bnVsbCwiZGVtb01vZGUiOmZhbHNlfQ"
        self.fake_instance_based_on_real_instance_visitor = "sF6lBbHgD6AH8BGJLuJ2Pb4jgAOlBG7xC7EP-kPzqMA.eyJpbnN0YW5jZUlkIjoiMTM4ZGVmZDgtNWU0Ni1hNDgyLTk0OGItMTJiMzdjNjZiYmFmIiwic2lnbkRhdGUiOiIyMDE0LTA4LTI2VDA0OjQ4OjE1Ljc2Ni0wNTowMCIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlwQW5kUG9ydCI6IjEwOC4yMjUuMTg5LjE3LzY0MDU3IiwidmVuZG9yUHJvZHVjdElkIjpudWxsLCJkZW1vTW9kZSI6ZmFsc2V9"
        self.real_instance_from_another_app_owner = "aZe-4vBFcrmVFwqkYy1ovPeiORg2wgcX-R9qzDjQUu8.eyJpbnN0YW5jZUlkIjoiMTM4ZGYwYTItNTAyMS1kNmZmLTQyODktNDMwZTA5ZjFiYTVjIiwic2lnbkRhdGUiOiIyMDE0LTA4LTI2VDA0OjUzOjU4LjM1Ny0wNTowMCIsInVpZCI6IjU0NjgzNWU1LWYyMzQtNDg3NC05NGQxLTcyMmJhZDI2YzY4OSIsInBlcm1pc3Npb25zIjoiT1dORVIiLCJpcEFuZFBvcnQiOiIxMDguMjI1LjE4OS4xNy81OTkwNiIsInZlbmRvclByb2R1Y3RJZCI6bnVsbCwiZGVtb01vZGUiOmZhbHNlfQ"
        self.real_instance_from_another_app_visitor = "nuviDrTaqBS8G32LdO5wsgtI6HHwTN-m0YKo6L3Yo3w.eyJpbnN0YW5jZUlkIjoiMTM4ZGYwYTItNTAyMS1kNmZmLTQyODktNDMwZTA5ZjFiYTVjIiwic2lnbkRhdGUiOiIyMDE0LTA4LTI2VDA0OjU3OjE1LjAyMC0wNTowMCIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlwQW5kUG9ydCI6IjEwOC4yMjUuMTg5LjE3LzU5MTk3IiwidmVuZG9yUHJvZHVjdElkIjpudWxsLCJkZW1vTW9kZSI6ZmFsc2V9"
        self.random_string_with_dot = "5fff5b6d-493f-4a37-94d1-268asdde23c8a1DSDZC.JDNJSNnsjkknjdfwJNAJnskajnkjnKJnjkanAJNNAKJnsjkndnadnwq09uwqdnKJDA9U00DnanskaxjADIOisaasadSJAiojiD89adaS90u0saUD8SNSNXSUHDA9S8ASU0A9JXA9DJXINAJKXNJJNJhjkdbjsbdjkabdu8ADdjkDBASYDBKdbjshd9q8whdXa80DHIa0DHIuiDBx8ADabxjY867A6xfaTYX5xra67XTaygxatx78ts7885d7yxgusigd87td78stcguUTC7s98s689dy89D89yxuis98d689DS89YX89xa89XY98ysxY8"
        self.random_string_without_dot = "5fff5b6d-493f-4a37-94d1-268asdde23c8a1DSDZCcJDNJSNnsjkknjdfwJNAJnskajnkjnKJnjkanAJNNAKJnsjkndnadnwq09uwqdnKJDA9U00DnanskaxjADIOisaasadSJAiojiD89adaS90u0saUD8SNSNXSUHDA9S8ASU0A9JXA9DJXINAJKXNJJNJhjkdbjsbdjkabdu8ADdjkDBASYDBKdbjshd9q8whdXa80DHIa0DHIuiDBx8ADabxjY867A6xfaTYX5xra67XTaygxatx78ts7885d7yxgusigd87td78stcguUTC7s98s689dy89D89yxuis98d689DS89YX89xa89XY98ysxY8"


class TestGetInstanceID(InstanceTestCase):
    def test_real_instance_owner(self):
        instance = self.real_instance_from_owner
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=True)
        self.assertIsInstance(result, self.result_type)
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=False)
        self.assertIsInstance(result, self.result_type)

    def test_real_instance_visitor(self):
        instance = self.real_instance_from_visitor
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=True)
        self.assertFalse(result)
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=False)
        self.assertIsInstance(result, self.result_type)

    def test_fake_instance_based_on_real_instance_owner(self):
        instance = self.fake_instance_based_on_real_instance_owner
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=True)
        self.assertFalse(result)
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=False)
        self.assertFalse(result)

    def test_fake_instance_based_on_real_instance_visitor(self):
        instance = self.fake_instance_based_on_real_instance_visitor
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=True)
        self.assertFalse(result)
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=False)
        self.assertFalse(result)

    def test_real_instance_from_another_app_owner(self):
        instance = self.real_instance_from_another_app_owner
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=True)
        self.assertFalse(result)
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=False)
        self.assertFalse(result)

    def test_real_instance_from_another_app_visitor(self):
        instance = self.real_instance_from_another_app_visitor
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=True)
        self.assertFalse(result)
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=False)
        self.assertFalse(result)

    def test_random_string_with_dot(self):
        instance = self.random_string_with_dot
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=True)
        self.assertFalse(result)
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=False)
        self.assertFalse(result)

    def test_random_string_without_dot(self):
        instance = self.random_string_without_dot
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=True)
        self.assertFalse(result)
        result = wixinstance.get_instance_ID(self.secret, instance,
                                             check_owner=False)
        self.assertFalse(result)


class TestGetInstanceObject(InstanceTestCase):
    def test_real_instance_owner(self):
        instance = self.real_instance_from_owner
        result = wixinstance.instance_parser(self.secret, instance)
        self.assertIsInstance(result, dict)

    def test_real_instance_visitor(self):
        instance = self.real_instance_from_visitor
        result = wixinstance.instance_parser(self.secret, instance)
        self.assertIsInstance(result, dict)

    def test_fake_instance_based_on_real_instance_owner(self):
        instance = self.fake_instance_based_on_real_instance_owner
        result = wixinstance.instance_parser(self.secret, instance)
        self.assertFalse(result)

    def test_fake_instance_based_on_real_instance_visitor(self):
        instance = self.fake_instance_based_on_real_instance_visitor
        result = wixinstance.instance_parser(self.secret, instance)
        self.assertFalse(result)

    def test_real_instance_from_another_app_owner(self):
        instance = self.real_instance_from_another_app_owner
        result = wixinstance.instance_parser(self.secret, instance)
        self.assertFalse(result)

    def test_real_instance_from_another_app_visitor(self):
        instance = self.real_instance_from_another_app_visitor
        result = wixinstance.instance_parser(self.secret, instance)
        self.assertFalse(result)

    def test_random_string_with_dot(self):
        instance = self.random_string_with_dot
        result = wixinstance.instance_parser(self.secret, instance)
        self.assertFalse(result)

    def test_random_string_without_dot(self):
        instance = self.random_string_without_dot
        result = wixinstance.instance_parser(self.secret, instance)
        self.assertFalse(result)

if __name__ == '__main__':
    main()
