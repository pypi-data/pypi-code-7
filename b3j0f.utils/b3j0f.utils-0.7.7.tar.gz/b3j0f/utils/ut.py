# -*- coding: utf-8 -*-

"""
Unit tests tools.
"""

from unittest import TestCase

from b3j0f.utils.version import PY26, PY27, PY3

from re import match

__all__ = ['UTCase']


class UTCase(TestCase):
    """
    Class which enrichs TestCase with python version compatibilities
    """

    def __init__(self, *args, **kwargs):

        super(UTCase, self).__init__(*args, **kwargs)

        if PY26:  # if python version is 2.6
            self.assertIs = lambda first, second, msg=None: self.assertTrue(
                first is second, msg=msg)
            self.assertIsNot = lambda first, second, msg=None: self.assertTrue(
                first is not second, msg=msg)
            self.assertIn = lambda first, second, msg=None: self.assertTrue(
                first in second, msg=msg)
            self.assertNotIn = lambda first, second, msg=None: self.assertTrue(
                first not in second, msg=msg)
            self.assertIsNone = lambda expr, msg=None: self.assertTrue(
                expr is None, msg=msg)
            self.assertIsNotNone = lambda expr, msg=None: self.assertFalse(
                expr is None, msg=msg)
            self.assertIsInstance = lambda obj, cls, msg=None: self.assertTrue(
                isinstance(obj, cls), msg=msg)
            self.assertNotIsInstance = lambda obj, cls, msg=None: \
                self.assertTrue(not isinstance(obj, cls), msg=msg)
            self.assertGreater = lambda first, second, msg=None: \
                self.assertTrue(first > second, msg=msg)
            self.assertGreaterEqual = lambda first, second, msg=None: \
                self.assertTrue(first >= second, msg=msg)
            self.assertLess = lambda first, second, msg=None: self.assertTrue(
                first < second, msg=msg)
            self.assertLessEqual = lambda first, second, msg=None: \
                self.assertTrue(first <= second, msg=msg)
            self.assertRegexpMatches = lambda text, regexp, msg=None: \
                self.assertTrue(
                    match(regexp, text)
                        if isinstance(regexp, str) else regexp.search(text),
                    msg=msg
                )
            # python 3 compatibility
            self.assertRegex = self.assertRegexpMatches
            self.assertNotRegexpMatches = lambda text, regexp, msg=None: \
                self.assertIsNone(
                    match(regexp, text)
                        if isinstance(regexp, str) else regexp.search(text),
                    msg=msg
                )
            # python 3 compatibility
            self.assertNotRegex = self.assertNotRegexpMatches
            self.assertItemsEqual = lambda actual, expected, msg=None: \
                self.assertEqual(sorted(actual), sorted(expected), msg=msg)

            def subset(a, b):
                result = True
                for k in a:
                    result = k in b and a[k] == b[k]
                    if not result:
                        break
                return result
            self.assertDictContainsSubset = lambda expected, actual, msg=None:\
                self.assertTrue(subset(expected, actual), msg=msg)
            self.assertCountEqual = lambda first, second, msg=None: \
                self.assertEqual(len(first), len(second), msg=msg)

        elif PY27:
            # python 3 compatibility
            self.assertRegex = self.assertRegexpMatches
            self.assertNotRegex = self.assertNotRegexpMatches

        elif PY3:
            #python 2 compatibility
            self.assertRegexpMatches = self.assertRegex
            self.assertNotRegexpMatches = self.assertNotRegex
            self.assertItemsEqual = lambda actual, expected, msg=None: \
                self.assertEqual(sorted(actual), sorted(expected), msg=msg)

            def subset(a, b):
                result = True
                for k in a:
                    result = k in b and a[k] == b[k]
                    if not result:
                        break
                return result
            self.assertDictContainsSubset = lambda expected, actual, msg=None:\
                self.assertTrue(subset(expected, actual), msg=msg)
