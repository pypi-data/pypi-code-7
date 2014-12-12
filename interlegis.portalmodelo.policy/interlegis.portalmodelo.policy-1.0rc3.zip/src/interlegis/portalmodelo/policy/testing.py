# -*- coding: utf-8 -*-

import os
from App.Common import package_home
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2


def loadFile(name, size=0):
    """Load file from testing directory
    """
    path = os.path.join(package_home(globals()), 'tests', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import interlegis.portalmodelo.policy
        self.loadZCML(package=interlegis.portalmodelo.policy)

        z2.installProduct(app, 'Products.AROfficeTransforms')
        z2.installProduct(app, 'Products.DateRecurringIndex')
        z2.installProduct(app, 'Products.EasyNewsletter')
        z2.installProduct(app, 'Products.Ploneboard')

    def setUpPloneSite(self, portal):
        # set the default workflow
        workflow_tool = portal['portal_workflow']
        workflow_tool.setDefaultChain('simple_publication_workflow')
        # XXX: plone-content profiles installs also portlets
        #      it should be better just to add the portlets instead
        #      of adding all content and then deleting it
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')
        # install the policy package
        self.applyProfile(portal, 'interlegis.portalmodelo.policy:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.AROfficeTransforms')
        z2.uninstallProduct(app, 'Products.DateRecurringIndex')
        z2.uninstallProduct(app, 'Products.EasyNewsletter')
        z2.uninstallProduct(app, 'Products.Ploneboard')

FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='interlegis.portalmodelo.policy:Integration')

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='interlegis.portalmodelo.policy:Functional')

ROBOT_TESTING = FunctionalTesting(
    bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name='interlegis.portalmodelo.policy:Robot',
)
