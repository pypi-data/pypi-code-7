from plone import api
from uuid import uuid4
from zope.security.management import newInteraction, endInteraction

from seantis.plonetools.testing import TestCase
from seantis.placemap.testing import (
    INTEGRATION_TESTING,
    FUNCTIONAL_TESTING
)


# to use with integration where security interactions need to be done manually
class IntegrationTestCase(TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        newInteraction()

    def tearDown(self):
        endInteraction()
        super(IntegrationTestCase, self).tearDown()

    def create_map(self, **kwargs):
        with self.user('admin'):
            return api.content.create(
                id=uuid4().hex,
                type='seantis.placemap.map',
                container=self.new_temporary_folder(),
                **kwargs
            )

    def create_source(self, map, **kwargs):
        with self.user('admin'):
            return api.content.create(
                id=uuid4().hex,
                type='seantis.placemap.source',
                container=map,
                **kwargs
            )


# to use with the browser which does its own security interactions
class FunctionalTestCase(TestCase):
    layer = FUNCTIONAL_TESTING
