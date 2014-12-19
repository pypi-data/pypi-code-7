from Products.Five.browser import BrowserView
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
import json


class CreateFolder(BrowserView):

	def __call__(self):

		if not self.request.get('new_id'):
			return json.dumps(False)

		title = self.request.get('new_id')

		#We want to clean up any "funny" folder ID's
		normalizer = getUtility(IIDNormalizer)
		folderId = normalizer.normalize(title)

		site = getSite()

		start = len(site.absolute_url())

		url = self.request.URL
		end = url.index('/@@create-folder')

		folderUrl = url[start:end]

		folders = folderUrl.split('/')

		here = site

		for folder in folders[1:]:
			here = here[folder]

		here.invokeFactory(type_name="Folder", id=folderId, title=title)

		if folderId in here:

			return json.dumps(True)
		else:
			return json.dumps(False)
