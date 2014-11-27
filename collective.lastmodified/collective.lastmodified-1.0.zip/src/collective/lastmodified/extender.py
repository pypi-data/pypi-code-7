from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.ATContentTypes.interface import IATDocument
from collective.lastmodified.interfaces import IAddOnInstalled
from collective.lastmodified.i18n import _


class ShowLastModifiedField(ExtensionField, BooleanField):
    """ Show Last Modified Field """


class DocumentExtender(object):
    adapts(IATDocument)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IAddOnInstalled

    fields = [
        ShowLastModifiedField(
            'showLastModified',
            schemata='settings',
            default=False,
            languageIndependent=True,
            widget = BooleanWidget(
                label=_(u"label_show_last_modified"),
                description=_(u"desc_show_last_modified"),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
