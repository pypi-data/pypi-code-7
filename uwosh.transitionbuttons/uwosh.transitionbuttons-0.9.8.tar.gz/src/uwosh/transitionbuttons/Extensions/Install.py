# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite

def uninstall(self, reinstall=False):
	if not reinstall:
		ps = getToolByName(self, 'portal_setup')

		ps.runAllImportStepsFromProfile('profile-uwosh.transitionbuttons:uninstall')
		_removeUserProperty(self)

		return "Uninstall successful."

def _removeUserProperty(portal):
	portal.portal_memberdata.manage_delProperties(['buttonsDisabled'])
	logger.info("User property removed")