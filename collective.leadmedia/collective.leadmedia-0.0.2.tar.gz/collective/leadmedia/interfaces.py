# Interfaces

from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer


class ILeadMediaSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class  ICanContainMedia(Interface):
    """
    This is a marker interface that aplies to all 
    """
    def getMedia(self):
        """
        Gets all media inside the folder
        """
        
    def hasMedia(self):
        """
        Checks if the current folder has media inside
        """
        
    def getLeadMedia(self):
        """
        Get the lead media
        """
