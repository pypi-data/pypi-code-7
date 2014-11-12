
# Viewlets
from plone.app.layout.viewlets import ViewletBase
from plone.dexterity.interfaces import IDexterityContainer
from plone.app.contenttypes.interfaces import IDocument
from Products.CMFCore.utils import getToolByName
from ..behaviors.slideshow import ISlideshow

class LeadMediaViewlet(ViewletBase):
    """ A simple viewlet which renders leadimage """

    def update(self):
    	# get item brain
    	catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.queryCatalog({"UID": self.context.UID()})
        item = brains[0]

        self.available = False

        if not ISlideshow.providedBy(self.context):
	        if hasattr(item, 'hasMedia'):
	        	if item.hasMedia:
	        		self.available = True
	        		media_brains = catalog.queryCatalog({"UID": item.leadMedia})
	        		media = media_brains[0]
	        		self.context.image = media.getObject()
	        	else:
	        		self.available = False

