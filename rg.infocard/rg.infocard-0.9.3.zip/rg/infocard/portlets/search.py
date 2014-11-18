# coding=utf-8
from .. import rg_infocard_logger as logger
from .. import rg_infocard_msgfactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
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
        required=False
    )

    target = schema.Choice(
        title=_(u"Target infocard container"),
        description=_(
            "help_target",
            u"Choose the infocard container in which you can search"
        ),
        source=SearchableTextSourceBinder({'portal_type': 'infocardcontainer'})
    )


@implementer(ISearchPortlet)
class Assignment(base.Assignment):

    """Portlet assignment."""

    def __init__(self, name='', target=None):
        self.name = name
        self.target = target

    @property
    def title(self):
        title = u"Infocard search"
        if self.data.name:
            title = u"%s: %s" % (title, self.data.name)
        return title


class AddForm(base.AddForm):
    form_fields = form.Fields(ISearchPortlet)
    label = _(u"Add Infocard search portlet")
    description = _(u"This portlet displays a search form.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ISearchPortlet)
    label = _(u"Edit Recent Portlet")
    description = _(u"This portlet displays a search form.")


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
