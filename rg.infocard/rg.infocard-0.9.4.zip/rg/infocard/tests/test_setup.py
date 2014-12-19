# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from rg.infocard.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of rg.infocard into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if rg.infocard is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('rg.infocard'))

    def test_uninstall(self):
        """Test if rg.infocard is cleanly uninstalled."""
        self.installer.uninstallProducts(['rg.infocard'])
        self.assertFalse(self.installer.isProductInstalled('rg.infocard'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IRgInfocardLayer is registered."""
        from rg.infocard.interfaces import IRgInfocardLayer
        from plone.browserlayer import utils
        self.failUnless(IRgInfocardLayer in utils.registered_layers())
