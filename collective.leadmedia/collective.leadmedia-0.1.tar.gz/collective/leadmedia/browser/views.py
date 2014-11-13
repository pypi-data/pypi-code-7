# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from zope.component import getUtility
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_inner
from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName

class FolderLeadMediaView(BrowserView):

    template = ViewPageTemplateFile('templates/folder_leadmedia_view.pt')

    def getImageObject(self, item):
    	if item.hasMedia:
	    	catalog = getToolByName(self.context, 'portal_catalog')
	    	media_brains = catalog.queryCatalog({"UID": item.leadMedia})
	    	media = media_brains[0]
	    	media_object = media.getObject()
	    	return media_object

class CollectionLeadMediaView(BrowserView):

    template = ViewPageTemplateFile('templates/collection_media_view.pt')

    def getImageObject(self, item):
    	if item.hasMedia:
	    	catalog = getToolByName(self.context, 'portal_catalog')
	    	media_brains = catalog.queryCatalog({"UID": item.leadMedia})
	    	media = media_brains[0]
	    	media_object = media.getObject()
	    	return media_object
    