import unittest
from Testing import ZopeTestCase as ztc
from plonehrm.contracts.tests.base import BaseTestCase


def test_suite():
    return unittest.TestSuite([
        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'doc/contracts-technical.txt', package='plonehrm.contracts',
            test_class=BaseTestCase),

        ztc.ZopeDocFileSuite(
            'doc/checkers.txt', package='plonehrm.contracts',
            test_class=BaseTestCase),

        ztc.ZopeDocTestSuite(
            module='plonehrm.contracts.content.tool',
            test_class=BaseTestCase),
    ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
