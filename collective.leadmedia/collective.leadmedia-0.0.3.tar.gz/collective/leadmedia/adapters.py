# Adapters

from zope.interface import implements
from collective.leadmedia.interfaces import ICanContainMedia
from Products.CMFCore.utils import getToolByName

class MediaHandling(object):
    implements(ICanContainMedia)

    def __init__(self, context):
        self.context = context

    def getMedia(self):
        """
        Get media 
        """
        item = self.context
        result = []

        if 'slideshow' in item.objectIds():
            slideshow = item['slideshow']
            for content in slideshow.getFolderContents():
                if content.portal_type == "Image":
                    result.append(content.getObject())
                    return result

                # If folderish content inside slideshow folder
                elif hasattr(content, 'meta_type'):
                    if content.meta_type == "Dexterity Container" and content.portal_type != "Folder":
                        if content.hasMedia:
                            content_object = content.getObject()
                            result.append(ICanContainMedia(content_object).getLeadMedia())
                            return result
            return result

        # No slideshow
        brains = item.getFolderContents()

        for brain in brains:
            if brain.portal_type == "Image":
                result.append(brain.getObject())
                return result

            # if folderish item inside item folder
            elif brain.meta_type == "Dexterity Container" and brain.portal_type != "Folder":
                if brain.hasMedia:
                    brain_object = brain.getObject()
                    result.append(ICanContainMedia(brain_object).getLeadMedia())
                    return result

        return result

    def hasMedia(self):
        """
        Check if item has media 
        """
        
        media = self.getMedia()

        if len(media) > 0:
            return True
        else:
            return False

    def getLeadMedia(self):
        """
        Get the lead media
        """

        media = self.getMedia()
        if len(media) > 0:
            return media[0]
        else:
            return None
