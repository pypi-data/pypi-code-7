from bise.catalogueindexer.interfaces import ICatalogueBase
from plone import api
from Products.Five.browser import BrowserView
from zope.component import queryAdapter

from requests import ConnectionError


class ContentIndexer(BrowserView):
    def __call__(self, *args, **kwargs):
        from logging import getLogger
        log = getLogger('ContentIndexer')

        for content in self.get_contents():
            adapter = queryAdapter(content, ICatalogueBase)
            if adapter is not None:
                try:
                    adapter.index_creation()
                except ConnectionError:
                    import time
                    time.sleep(3)
                    try:
                        adapter.index_creation()
                    except ConnectionError:
                        log.info('Error indexing')
                        continue
                log.info('Content indexed: {0}'.format(
                    content.getPhysicalPath()
                    )
                )
            else:
                log.info('Not indexed: {0}'.format(
                    content.getPhysicalPath()
                    )
                )
        return 1

    def get_contents(self):
        catalog = api.portal.get_tool('portal_catalog')
        contents = catalog(portal_type='BiodiversityFactsheet')
        for content in contents:
            yield content.getObject()
