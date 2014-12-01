from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import quickInstallProduct

from plone.testing import z2
from Testing import ZopeTestCase
from zope.configuration import xmlconfig


class TestLayer(PloneSandboxLayer):

    default_bases = (PLONE_FIXTURE,)

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def setUpZope(self, app, configurationContext):

        # Set up sessioning objects
        app.REQUEST['SESSION'] = self.Session()
        ZopeTestCase.utils.setupCoreSessions(app)

        import seantis.plonetools
        self.loadZCML(package=seantis.plonetools)

        import seantis.placemap
        self.loadZCML(package=seantis.placemap)

        xmlconfig.file(
            'configure.zcml',
            seantis.placemap,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        quickInstallProduct(portal, 'seantis.placemap')
        applyProfile(portal, 'seantis.placemap:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'seantis.placemap')


TESTFIXTURE = TestLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(TESTFIXTURE, ),
    name="Testfixture:Integration"
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(TESTFIXTURE, ),
    name="Testfixture:Functional"
)
