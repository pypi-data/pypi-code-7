# -*- coding: utf-8 -*-
from collective.pdfpeek import testing
from collective.pdfpeek.tests.test_atfiles import TestATDataExtraction
from plone.app.contenttypes.interfaces import IFile
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile


class TestDxDataExtraction(TestATDataExtraction):
    """Unit tests for the transformation and metadata extraction of PDF files
       stored in dexterity file objects of ``plone.app.contenttypes``.
    """

    layer = testing.PDFPEEK_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        # Create files
        for uri in self.layer['pdf_files']:
            content_id = uri.split('/').pop()
            blobfile = NamedBlobFile(filename=unicode(content_id),
                                     data=open(uri, 'r').read())

            dxfile = createContentInContainer(
                self.portal, 'File', id=content_id, file=blobfile)

            self.assertTrue(IFile.providedBy(dxfile))

        self._validate_created_files()
        logout()
