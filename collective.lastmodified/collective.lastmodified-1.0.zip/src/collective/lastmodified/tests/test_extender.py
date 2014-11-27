import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.lastmodified.testing import \
    COLLECTIVE_LASTMODIFIED_INTEGRATION_TESTING


class TestExample(unittest.TestCase):

    layer = COLLECTIVE_LASTMODIFIED_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('Document', 'test-document')
        self.document = self.folder['test-document']

    def test_folder_has_no_injected_field(self):
        schema = self.folder.Schema()
        self.assertEquals(schema.getField('showLastModified'), None)

    def test_document_has_injected_field(self):
        schema = self.document.Schema()
        self.assertTrue(schema.getField('showLastModified'))
