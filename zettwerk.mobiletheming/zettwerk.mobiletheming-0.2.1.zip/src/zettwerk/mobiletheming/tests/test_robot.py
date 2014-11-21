from  zettwerk.mobiletheming.testing import ZETTWERK_MOBILETHEMING_FUNCTIONAL_TESTING
from plone.testing import layered
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("robot_test.txt"),
                layer=ZETTWERK_MOBILETHEMING_FUNCTIONAL_TESTING)
    ])
    return suite