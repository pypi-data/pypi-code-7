# -*- coding: utf-8 -*-
from plone.app.testing import IntegrationTesting
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone import api


class GlobalGopipIndexLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def _patch(self):
        import experimental.globalgopipindex
        self.loadZCML(package=experimental.globalgopipindex)

    def setUpZope(self, app, configurationContext):
        self['patch'] = self._patch

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Contributor'])
        a = api.content.create(
            type='Folder',
            title='A',
            container=portal
        )
        for i in range(3):
            api.content.create(
                type='Document',
                title='A{0:d}'.format(i + 1),
                container=a
            )
        b = api.content.create(
            type='Folder',
            title='B',
            container=portal
        )
        for i in range(3):
            api.content.create(
                type='Document',
                title='B{0:d}'.format(i + 1),
                container=b
            )


GOPIPINDEX_FIXTURE = GlobalGopipIndexLayer()

GOPIPINDEX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GOPIPINDEX_FIXTURE,),
    name="GlobalGopipIndex:Integration")
