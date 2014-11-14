from plone.portlets.interfaces import IPortletType, IPortletAssignment,\
    IPortletDataProvider, IPortletManager, IPortletRenderer
from zope.component import getUtility, getMultiAdapter
from plone.testing import z2

from collective.portlet.pythonscript.tests.base import TestBase
from collective.portlet.pythonscript.content.interface import IPythonScriptManager

from collective.viewlet.pythonscript.browser.viewlet import PythonScriptViewlet

class TestPortlet(TestBase):
    """Test script portlet."""

    def setUp(self):
        """Login as manager."""
        super(TestPortlet, self).setUp()
        z2.login(self.app['acl_users'], 'admin')
        self.addPythonScript('first', u'First', 'return []')
        self.addPythonScript('second', u'Second', 'return []')
        self.addPythonScript('third', u'Third', u"""
from Products.CMFCore.utils import getToolByName
portal_catalog = getToolByName(context, 'portal_catalog')
return portal_catalog()""")
        self.addPythonScript('fourth', u'Fourth', u"""
from Products.CMFCore.utils import getToolByName
portal_catalog = getToolByName(context, 'portal_catalog')
return {'results':portal_catalog(), 'text':'Additional text', 'icon_url': '/link/to/icon.png'}
""")
        manager = IPythonScriptManager(self.portal)
        manager.rescanScripts()
        manager.enableScript('/plone/second')
        manager.enableScript('/plone/third')
        manager.enableScript('/plone/fourth')

        self.portal.invokeFactory("Folder", "folder")
        folder = self.portal.folder
        folder.setTitle(u'Folder')
        folder.invokeFactory("Folder", "subfolder")
        subfolder = folder.subfolder
        subfolder.setTitle(u'Subfolder')
        subfolder.invokeFactory("Document", "doc")
        doc = subfolder.doc
        doc.setTitle(u'Document')

    def tearDown(self):
        """Logout."""
        super(TestPortlet, self).tearDown()
        z2.logout()

    # TODO: write scripts
    def testViewletRegistered(self):
        #PythonScriptViewlet(self.portal, self.portal.REQUEST, None, None)
        pass

