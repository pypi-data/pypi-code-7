from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class ZettwerkmobilethemingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import zettwerk.mobiletheming
        xmlconfig.file(
            'configure.zcml',
            zettwerk.mobiletheming,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'zettwerk.mobiletheming:default')

ZETTWERK_MOBILETHEMING_FIXTURE = ZettwerkmobilethemingLayer()
ZETTWERK_MOBILETHEMING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ZETTWERK_MOBILETHEMING_FIXTURE,),
    name="ZettwerkmobilethemingLayer:Integration"
)
ZETTWERK_MOBILETHEMING_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ZETTWERK_MOBILETHEMING_FIXTURE, z2.ZSERVER_FIXTURE),
    name="ZettwerkmobilethemingLayer:Functional"
)
