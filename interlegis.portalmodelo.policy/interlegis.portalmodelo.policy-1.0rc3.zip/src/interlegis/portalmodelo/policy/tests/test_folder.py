# -*- coding: utf-8 -*-
from interlegis.portalmodelo.policy.testing import INTEGRATION_TESTING

import unittest


class FolderViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.types = self.portal['portal_types']

    def test_default_view(self):
        folder = self.types['Folder']
        self.assertEqual(folder.default_view, 'folder_summary_view')
