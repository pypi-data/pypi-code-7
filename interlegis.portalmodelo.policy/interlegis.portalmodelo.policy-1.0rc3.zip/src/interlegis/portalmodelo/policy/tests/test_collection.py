# -*- coding: utf-8 -*-
from interlegis.portalmodelo.policy.testing import INTEGRATION_TESTING

import unittest


class CollectionViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.types = self.portal['portal_types']

    def test_default_view(self):
        collection = self.types['Collection']
        self.assertEqual(collection.default_view, 'summary_view')
