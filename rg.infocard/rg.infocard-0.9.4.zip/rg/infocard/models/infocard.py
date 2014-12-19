# -*- coding: utf-8 -*-
from .base import IInfocardComplexField, InfocardDataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from plone.supermodel.model import Schema
from plone.dexterity.content import Container
from plone.directives import form
from rg.infocard import rg_infocard_msgfactory as _
from rg.infocard.vocs.infocard_servicetypes import InfocardServicetypes
from rg.infocard.vocs.infocard_recipients import InfocardRecipients
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope.interface import implementer
from zope import schema


class IInfocard(Schema):
    form.model('infocard.xml')
    servicetypes = schema.Tuple(
        title=_(
            'label_servicetypes',
            u"Service types"
        ),
        value_type=schema.Choice(
            source=InfocardServicetypes
        ),
        default=(),
        required=True,
    )
    recipients = schema.Tuple(
        title=_(
            'label_recipients',
            u"Recipients"
        ),
        value_type=schema.Choice(
            source=InfocardRecipients,
        ),
        default=(),
        required=True,
    )
    informations = schema.List(
        title=_(
            'label_informations',
            u"Informations"
        ),
        value_type=DictRow(
            title=_(u"infocard_info", "Info"),
            schema=IInfocardComplexField,
        ),
        required=False,
        default=[],
        missing_value=[]
    )
    form.widget(informations=InfocardDataGridFieldFactory)
    form.widget(servicetypes=CheckBoxFieldWidget)
    form.widget(recipients=CheckBoxFieldWidget)


@form.default_value(field=IInfocard['informations'])
def default_informations(data):
    ''' Use the parent informations
    '''
    from rg.infocard.models.infocardcontainer import Infocardcontainer
    for obj in data.context.aq_chain:
        if isinstance(obj, Infocardcontainer):
            return obj.informations
    return []


@implementer(IInfocard)
class Infocard(Container):
    '''
    Infocard class
    '''
    exclude_from_nav = True
