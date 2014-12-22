
# python standard library
import unittest

# this package
from ape.parts.dummy.dummy import CrashDummy
from ape import ApeError


class TestCrashDummy(unittest.TestCase):
    def setUp(self):
        self.error = ApeError
        self.error_message = 'ummagumma'
        self.function = 'close'
        self.extra_key = 'aoeu'
        self.extra_value = 1234
        self.extra = {self.extra_key: self.extra_value}

        self.dummy = CrashDummy(error=self.error,
                                error_message=self.error_message,
                                function = self.function,
            **self.extra)
        return

    def test_constructor(self):
        """
        Does the signature match expectations?
        """
        self.assertEqual(self.error, self.dummy.error)
        self.assertEqual(self.error_message, self.dummy.error_message)
        self.assertEqual(self.function, self.dummy.function)
        self.assertEqual(self.extra_value, self.dummy.aoeu)
        return

    def test_constructor_crash(self):
        """
        If the function is __init__ will it crash on construction?
        """
        with self.assertRaises(RuntimeError):
            CrashDummy(error=RuntimeError,
                       error_message='crash',
                       function=CrashDummy.INIT)
        return

    def test_close_crash(self):
        """
        If the function is 'close' will it crash?
        """
        self.dummy.function = 'close'
        with self.assertRaises(self.error):
            self.dummy.close()
        return

    def test_check_rep_crash(self):
        """
        If the function is 'check_rep' will it crash?
        """
        self.dummy.function = 'check_rep'
        with self.assertRaises(self.error):
            self.dummy.check_rep()
        return

    def test_call_crash(self):
        """
        If the function is '__call__' will it crash?
        """
        self.dummy.function = '__call__'
        with self.assertRaises(self.error):
            self.dummy()
        return

    def test_extra(self):
        """
        If I add a function name will it crash?
        """
        self.dummy.function = 'abbadabba'
        with self.assertRaises(self.error):
            self.dummy.abbadabba()
        return
