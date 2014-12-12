#from Acquisition import aq_inner
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from Products.Five import BrowserView

import urllib 

class RedirectView(BrowserView):
        
    def __call__(self, index='kortnummer', index_value=''):
        """redirect to indexed content"""
                
        catalog = api.portal.get_tool(name='portal_catalog')

        query = {index: index_value.decode('latin-1')} 
        content_items = catalog(**query) 

        if len(content_items) == 1:
            content_url = content_items[0].getURL()
            return self.context.REQUEST.RESPONSE.redirect(content_url)
        
        #nothing, or too much found... search for it
        search_url = '/@@search?' +index + '=' + index_value
        return self.context.REQUEST.RESPONSE.redirect(search_url)
