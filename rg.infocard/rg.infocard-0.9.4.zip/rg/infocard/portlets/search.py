# coding=utf-8
from .. import rg_infocard_logger as logger
from .. import rg_infocard_msgfactory as _
from ..vocs.infocard_servicetypes import InfocardServicetypes
from ..vocs.infocard_recipients import InfocardRecipients
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope.formlib import form
from zope.interface import implementer
from zope import schema


class ISearchPortlet(IPortletDataProvider):

    """A portlet that allows searching in an infocard container
    """
    name = schema.TextLine(
        title=_(u"name", default=u"Portlet name"),
        default=u'Infocard search portlet',
        required=False,
    )

    display_title = schema.Bool(
        title=_(u"label_display_title", default=u"Display title"),
        description=_(
            u"help_display_title",
            u"If checked the portlet will display a title based on name"
        ),
        default=True,
        required=True,
    )

    target = schema.Choice(
        title=_(u"Target infocard container"),
        description=_(
            "help_target",
            u"Choose the infocard container in which you can search"
        ),
        source=SearchableTextSourceBinder({'portal_type': 'infocardcontainer'})
    )

    display_filters = schema.Bool(
        title=_('label_display_filters', u"Display filters"),
        description=_(
            "help_display_filters",
            u'By default the portlet displays one input '
            u'to search on infocard text. '
            u'If you select this checkbox two additional selects will appear. '
            u'They will allow to search in the fields '
            u'"Service type" and "Recipient".'
        ),
        default=False,
    )

    text_before = schema.Text(
        title=_(u"Text before search fields"),
        description=_(u"This text will appear before the search fields"),
        required=False
    )

    text_after = schema.Text(
        title=_(u"Text after search fields"),
        description=_(u"This text will appear after the search fields"),
        required=False
    )


@implementer(ISearchPortlet)
class Assignment(base.Assignment):

    """Portlet assignment."""

    def __init__(
        self,
        name=u'',
        display_title=True,
        target=None,
        display_filters=False,
        text_before=u"",
        text_after=u""
    ):
        self.name = name
        self.display_title = display_title
        self.target = target
        self.display_filters = display_filters
        self.text_before = text_before
        self.text_after = text_after

    @property
    def title(self):
        title = u"Infocard search"
        if self.data.name:
            title = u"%s: %s" % (title, self.data.name)
        return title


class AddForm(base.AddForm):
    label = _(u"Add Infocard search portlet")
    description = _(u"This portlet displays a search form.")
    schema = ISearchPortlet
    form_fields = form.Fields(schema)
    form_fields['text_after'].custom_widget = WYSIWYGWidget
    form_fields['text_before'].custom_widget = WYSIWYGWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    label = _(u"Edit Recent Portlet")
    description = _(u"This portlet displays a search form.")
    schema = ISearchPortlet
    form_fields = form.Fields(schema)
    form_fields['text_after'].custom_widget = WYSIWYGWidget
    form_fields['text_before'].custom_widget = WYSIWYGWidget


class Renderer(base.Renderer):

    ''' Render he search form
    '''
    render = ViewPageTemplateFile('search.pt')

    @memoize
    def available(self):
        '''
        The portlet will be available if the target is visible
        '''
        return all(
            self.target,
            'View' in api.user.get_permissions(obj=self.target),
        )

    @property
    @memoize
    def target(self):
        ''' Get's the object related to the target
        '''
        try:
            return api.portal.get().unrestrictedTraverse(self.data.target[1:])
        except:
            msg = "Unable to find target: %s" % self.data.target
            logger.exception(msg)

    @property
    @memoize
    def display_title(self):
        ''' Check out the configuration to see if we can display title
        '''
        return self.data.display_title

    @property
    @memoize
    def text_before(self):
        ''' Display text before search fields
        '''
        return self.data.text_before

    @property
    @memoize
    def text_after(self):
        ''' Display text after search fields
        '''
        return self.data.text_after

    @property
    @memoize
    def display_filters(self):
        ''' Check out the configuration to see if we can display additional
        checkboxes for filtering on recipents and service types
        '''
        return self.data.display_filters

    @property
    @memoize
    def recipients(self):
        ''' Get the recipient vocabulary for target
        '''
        return InfocardRecipients(self.target)

    @property
    @memoize
    def servicetypes(self):
        ''' Get the recipient vocabulary for target
        '''
        return InfocardServicetypes(self.target)
