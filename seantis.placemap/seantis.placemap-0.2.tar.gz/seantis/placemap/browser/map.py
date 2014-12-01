import logging
log = logging.getLogger('seantis.placemap')

from collective.geo.mapwidget.browser.widget import MapWidget
from five import grok
from plone import api
from plone.memoize.view import memoize
from uuid import uuid4
from zope.security import checkPermission
from zExceptions import NotFound

from seantis.plonetools import async
from seantis.plonetools import unrestricted

from seantis.placemap import utils
from seantis.placemap.browser import BaseView
from seantis.placemap.browser.sourcelayer import SourceLayer
from seantis.placemap.interfaces import IMap


secret_key = uuid4().hex
log.info("The secret key to access the update-sources views is {}".format(
    secret_key
))


class MapBaseView(BaseView):

    grok.baseclass()

    @memoize
    def get_sources(self):
        folder_path = '/'.join(self.context.getPhysicalPath())
        catalog = api.portal.get_tool('portal_catalog')

        return catalog(
            path={'query': folder_path, 'depth': 1},
            portal_type='seantis.placemap.source'
        )


class UpdateSources(MapBaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(IMap)
    grok.name(secret_key)

    def update_sources(self):
        with unrestricted.run_as('Manager'):
            for source in (b.getObject() for b in self.get_sources()):

                # Be careful here, this url could be something that the
                # user is not allowed to look at. For now it needs to be parsed
                # kml, but if this ever changes there might security problems.
                kml = utils.fetch_kml_document(source.url)

                if kml:
                    source.kml = utils.translate_kml_document(
                        self.request, kml
                    )
                else:
                    raise NotFound()

    def render(self):
        self.request.response.setHeader("Content-type", "text/plain")
        self.update_sources()
        return u'done'


class MapView(MapBaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(IMap)
    grok.name('view')

    template = grok.PageTemplateFile('templates/map.pt')

    @property
    def show_map(self):
        return len(self.get_sources()) > 0

    @property
    def is_public(self):
        workflow_tool = api.portal.get_tool('portal_workflow')
        review_state = workflow_tool.getInfoFor(self.context, 'review_state')

        return review_state == 'published'

    @property
    def show_controls(self):
        """ Returns True if the sources should be modifyable/removeable. """

        # not exactly the required permission, but that's not the point:
        # if the user has the permission to edit the context the permission
        # to edit the sources probably inherited.
        return checkPermission('cmf.ModifyPortalContent', self.context)

    @property
    def mapfields(self):
        assert self.show_map, """
            This should not be called if there are no sources.
        """

        widget = MapWidget(self, self.request, self.context)
        widget._layers = tuple(
            SourceLayer.from_source(s) for s in self.get_sources()
        )

        return (widget, )

    def get_item_state(self, item):
        workflow = api.portal.get_tool('portal_workflow')

        return workflow.getTitleForStateOnType(
            item.review_state, item.portal_type
        )

    def update(self):
        super(MapView, self).update()

        update_path = '{}/{}'.format(
            '/'.join(self.context.getPhysicalPath()), secret_key
        )

        # run the update hourly
        async.register(update_path, 3600)
