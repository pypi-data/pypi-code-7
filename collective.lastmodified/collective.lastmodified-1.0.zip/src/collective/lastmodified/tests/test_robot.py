from  collective.lastmodified.testing import \
    COLLECTIVE_LASTMODIFIED_FUNCTIONAL_TESTING
from plone.testing import layered
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("lastmodified.robot"),
                layer=COLLECTIVE_LASTMODIFIED_FUNCTIONAL_TESTING)
    ])
    return suite
