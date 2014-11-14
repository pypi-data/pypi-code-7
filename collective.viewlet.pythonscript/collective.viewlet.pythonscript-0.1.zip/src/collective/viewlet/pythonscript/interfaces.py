from zope.interface import Interface
from collective.portlet.pythonscript.browser.renderer import IResultsRenderer

class IViewletConfigFieldsExtender(Interface):
    """ Marker interface for content types extending viewlet configuration fields """


class IViewletResultsRenderer(IResultsRenderer):
    """ Marker interface for the views displaying viewlets results """