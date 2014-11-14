from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

from collective.viewlet.pythonscript.interfaces import IViewletResultsRenderer

class DefaultListing(BrowserView):
    """ """

    implements(IViewletResultsRenderer)

    title = _(u"Default listing")

    template = ViewPageTemplateFile('default_listing.pt')

    def __call__(self, results, **kwargs):
        """Render results."""
        return self.template(results=results, **kwargs)
