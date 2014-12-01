import unittest2 as unittest
from plone.app.testing import setRoles, login, TEST_USER_NAME

from uwosh.transitionbuttons.testing import BaseTest
from uwosh.transitionbuttons.controlpanel import ButtonSettingsControlPanel as Base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView as View

from uwosh.transitionbuttons.testing import \
    UWOSH_TRANSITIONBUTTONS_FUNCTIONAL_TESTING


class TestControlPanel(BaseTest):

    layer = UWOSH_TRANSITIONBUTTONS_FUNCTIONAL_TESTING

    def test_exists(self):
        portal = self.layer['portal']
        browser = self.browser
        self.getControlPanel()
        element = browser.getControl('Site element.').value
        self.assertTrue(element != "")

    def test_saves(self):
        portal = self.layer['portal']
        browser = self.browser
        self.getControlPanel()
        browser.getControl('Site element.').value = u"empty"
        browser.getControl('Save').click()

        self.assertTrue(browser.getControl('Site element.').value == "empty")

    def test_viewlet_sees_changes(self):
        portal = self.layer['portal']
        browser = self.browser
        self.getControlPanel()
        browser.getControl('Site element.').value = u"empty"
        browser.getControl('Save').click()

        bv = self.buttonViewlet
        settings = bv.getSettings()

        self.assertTrue(settings.pageElement == u"empty")

    def test_isFixed(self):
        portal = self.layer['portal']
        browser = self.browser
        self.getControlPanel()
        browser.getControl('Floating button box.').selected = True
        browser.getControl('Save').click()

        bv = self.buttonViewlet
        settings = bv.getSettings()

        self.assertTrue(settings.floating == True)


