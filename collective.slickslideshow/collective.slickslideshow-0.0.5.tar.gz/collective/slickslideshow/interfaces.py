# Interfaces

from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer


class ISlickSlideshowSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
