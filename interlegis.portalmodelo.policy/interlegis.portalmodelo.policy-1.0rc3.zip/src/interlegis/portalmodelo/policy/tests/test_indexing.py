# -*- coding: utf-8 -*-

from interlegis.portalmodelo.policy.testing import INTEGRATION_TESTING
from interlegis.portalmodelo.policy.testing import loadFile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class FileIndexingTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']

    def test_pdf(self):
        self.folder.invokeFactory('File', 'test_file')
        self.folder.test_file.setFile(loadFile('test.pdf'))
        self.folder.test_file.reindexObject()
        results = self.portal.portal_catalog(SearchableText='vovo')
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].id == 'test_file')
        results = self.portal.portal_catalog(SearchableText='vovô')
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].id == 'test_file')

    # For some reason word splitter is broken for this portal transformation
    @unittest.skip('Issue with word splitter in travis-ci')
    def test_odt(self):
        self.folder.invokeFactory('File', 'test_file')
        self.folder.test_file.setFile(
            loadFile('test.odt'),
            mimetype='application/vnd.oasis.opendocument.text')
        self.folder.test_file.reindexObject()
        results = self.portal.portal_catalog(SearchableText='vovo')
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].id == 'test_file')
        results = self.portal.portal_catalog(SearchableText='vovô')
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].id == 'test_file')

    # For some reason word splitter is broken for this portal transformation
    @unittest.skip('Issue with word splitter in travis-ci')
    def test_doc(self):
        self.folder.invokeFactory('File', 'test_file')
        self.folder.test_file.setFile(loadFile('test.doc'))
        self.folder.test_file.reindexObject()
        results = self.portal.portal_catalog(SearchableText='vovo')
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].id == 'test_file')
        results = self.portal.portal_catalog(SearchableText='vovô')
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].id == 'test_file')

    def test_docx(self):
        self.folder.invokeFactory('File', 'test_file')
        self.folder.test_file.setFile(
            loadFile('test.docx'),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.folder.test_file.reindexObject()
        results = self.portal.portal_catalog(SearchableText='vovo')
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].id == 'test_file')
        results = self.portal.portal_catalog(SearchableText='vovô')
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].id == 'test_file')
