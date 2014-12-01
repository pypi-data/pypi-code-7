from five import grok
from plone.autoform.form import AutoExtensibleForm
from plone.directives.dexterity import AddForm

from seantis.placemap import _
from seantis.placemap import utils
from seantis.placemap.browser.base import BaseForm, BaseView
from seantis.placemap.interfaces import ISource


class SourceBaseForm(BaseForm, AutoExtensibleForm):

    grok.baseclass()

    @property
    def cancel_url(self):
        return self.success_url

    def before_save(self, data):
        kml = utils.fetch_kml_document(data['url'])

        if kml:
            data['kml'] = utils.translate_kml_document(self.request, kml)
        else:
            self.raise_action_error(
                _(u"No KML-Document was found on the given url")
            )


class SourceAddForm(AddForm, SourceBaseForm):
    grok.name('seantis.placemap.source')

    grok.context(ISource)
    grok.require('cmf.AddPortalContent')

    schema = ISource

    @property
    def success_url(self):
        return self.context.absolute_url()


class SourceEditForm(SourceBaseForm):
    """ Provides an edit form for memberships in seantis.kantonsrat. Said
    form does not offer all fields. It namely removes the ability to change
    the referenced person.

    """
    grok.name('edit')

    grok.context(ISource)
    grok.require('cmf.ModifyPortalContent')

    schema = ISource

    @property
    def success_url(self):
        return self.context.aq_inner.aq_parent.absolute_url()


class SourceKmlView(BaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(ISource)
    grok.name('kml-document')

    def render(self):
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="%s"' % self.context.id
        )
        self.request.response.setHeader(
            'Content-Type',
            'application/vnd.google-earth.kml+xml; charset=utf-8'
        )

        return self.context.kml
