# -*- coding: utf-8 -*-
from .base import IInfocardComplexField, InfocardDataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.directives import form
from plone.supermodel.model import Schema
from rg.infocard import rg_infocard_msgfactory as _
from zope.interface import implementer
from zope import schema


class IInfocardcontainer(Schema):
    form.model('infocardcontainer.xml')

    introduction = RichText(
        title=_(
            'label_introduction',
            u"Introduction"
        ),
        description=_(
            'help_search_introduction',
            (
                u"This text will appear before the container search form"
            )
        ),
    )

    servicetypes = schema.List(
        title=_(
            'label_available_servicetypes',
            u"Available service types"
        ),
        description=_(
            'help_available_servicetypes',
            (
                u"Insert one service type per line. "
                u"They will be proposed "
                u"in the service type field of the infocards"
            )
        ),
        value_type=schema.TextLine(
            title=_(u"service_type", "Service type")
        ),
        default=[],
        required=True,
    )

    recipients = schema.Tuple(
        title=_(
            'label_available_recipients',
            u"Available recipients"
        ),
        description=_(
            'help_available_recipients',
            (
                u"Insert one recipient per line. "
                u"They will be proposed "
                u"in the recipient field of the infocards"
            )
        ),
        value_type=schema.TextLine(
            title=_(u"recipient", "Recipient")
        ),
        default=(),
        required=True,
    )
    informations = schema.List(
        title=_(
            'label_default_infos',
            u"List of default informations"
        ),
        description=_(
            'help_default_infos',
            (
                u"The informartions listed below "
                u"will be used as a default for the new infocard"
            )
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


@implementer(IInfocardcontainer)
class Infocardcontainer(Container):
    '''
    Infocardcontainer class
    '''
