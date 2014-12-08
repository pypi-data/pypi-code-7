from Products.PloneTestCase import PloneTestCase as ptc
from Products.plonehrm.tests.base import PlonehrmLayer

ptc.setupPloneSite()


class BaseTestCase(ptc.PloneTestCase):
    layer = PlonehrmLayer
