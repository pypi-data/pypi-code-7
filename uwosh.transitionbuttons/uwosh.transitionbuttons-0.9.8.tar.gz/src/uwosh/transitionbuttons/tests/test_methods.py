import unittest2 as unittest
from plone.app.testing import setRoles, login, TEST_USER_NAME

from uwosh.transitionbuttons.testing import BaseTest

from Products.CMFCore.utils import getToolByName
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager
from Products.Five.browser import BrowserView as View

from uwosh.transitionbuttons.browser.viewlets import ButtonViewlet
import Products.DCWorkflow as wftool

from uwosh.transitionbuttons.testing import \
    UWOSH_TRANSITIONBUTTONS_FUNCTIONAL_TESTING


class TestMethods(BaseTest):

    layer = UWOSH_TRANSITIONBUTTONS_FUNCTIONAL_TESTING

    def test_installed(self):
    	portal = self.layer['portal']
    	installer = getToolByName(portal, 'portal_quickinstaller')
    	self.assertTrue(installer.isProductInstalled('uwosh.transitionbuttons'))

    def test_js(self):
    	portal = self.layer['portal']
    	js_reg = getToolByName(portal, 'portal_javascripts')
    	self.assertTrue('++resource++transitionbuttons.js' in js_reg.getResourceIds())

    def test_css(self):
        portal = self.layer['portal']
        css_reg = getToolByName(portal, 'portal_css')
        self.assertTrue('++resource++buttons.css' in css_reg.getResourceIds())

    def test_isPanelEnabled(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

        bv = self.buttonViewlet
        isDisabled = bv.isPanelDisabled()
        self.assertFalse(isDisabled)

    def test_isPanelAllowed(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

        bv = self.buttonViewlet
        allowed = bv.isPanelAllowed()
        self.assertTrue(allowed)

    def test_getWFStateself(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

        bv = self.buttonViewlet
        state = bv.getWFState()
        self.assertEqual(state, 'private')

    def test_getSettings(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

        bv = self.buttonViewlet
        settings = bv.getSettings()
        self.assertIsNotNone(settings)

    def test_getStateDescription(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        bv = self.buttonViewlet
        desc = bv.getStateDescription()
        self.assertEqual(desc, 'Can only be seen and edited by the owner.')

    def test_setJson(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

        bv = self.buttonViewlet
        json = bv.setJson()
        self.assertIsNotNone(json)

    def test_getSite(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

        bv = self.buttonViewlet
        site = bv.getSite()
        self.assertEqual(site, 'http://nohost/plone')

    def test_getPreferencesUrl(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

        bv = self.buttonViewlet
        url = bv.getPreferencesUrl()
        self.assertEqual(url, 'http://nohost/plone/@@personal-preferences')

    def test_viewletPresent(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

        bv = self.buttonViewlet
        docUrl = self.doc.absolute_url()
        browser = self.browser
        browser.open(docUrl)
        self.assertTrue('js_info' in browser.contents)



