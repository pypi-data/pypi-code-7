
from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import public as atapi
from Products.CMFPlone import PloneMessageFactory as _

from collective.viewlet.pythonscript.interfaces import IViewletConfigFieldsExtender

class ExtensionBooleanField(ExtensionField, atapi.BooleanField):
    """ Extension boolean field """


class ExtensionInheritanceField(ExtensionField):
    """ Extension field taking into accout the inheritance settings """

    def get(self, instance, **kwargs):
        inherit = getattr(instance, 'inherit_viewlet_settings', False)
        if kwargs.get('inherit'):
            inherit = kwargs.pop('inherit')
        field = kwargs.get('field')
        if inherit:
            try:
                instance = instance.aq_inner.aq_parent
            except AttributeError:
                return None
            value = self.get(instance, **kwargs)
            return value
        try:
            value = self.getStorage(instance).get(self.getName(), instance, **kwargs)
        except AttributeError:
            value = self.default
        return value


class ExtensionStringField(ExtensionInheritanceField, atapi.StringField):
    """ Extension string field """


class ExtensionIntField(ExtensionInheritanceField, atapi.IntegerField):
    """ Extension integer field """


class ViewletConfigFieldsExtender(object):
    adapts(IViewletConfigFieldsExtender)
    implements(ISchemaExtender)

    fields = [
        ExtensionBooleanField(
        	"inherit_viewlet_settings",
        	schemata = "Listing",
        	widget = atapi.BooleanWidget(
            	label=_(u"Inherit viewlet settinngs"),
            	description=_(u"If checked - the settings will be inherited from parent."),
            ),
        ),
        ExtensionStringField(
        	"viewlet_title",
        	schemata = "Listing",
        	widget = atapi.StringWidget(
            	label=_(u"Viewlet title"),
            ),
        ),
        ExtensionStringField(
        	"script_name",
        	vocabulary_factory = "python-scripts-viewlet",
        	schemata = "Listing",
            required = False,
        	widget = atapi.SelectionWidget(
                format='select',
            	label=_(u"Python Script"),
            	description=_(u"Python Script used to generate list of results"),
            ),
        ),
        ExtensionIntField(
        	"limit_results",
        	schemata = "Listing",
        	widget = atapi.IntegerWidget(
            	label=_(u"Limit results"),
            	description=_(u"How many results should be displayed (none means all)"),
            ),
        ),
        ExtensionStringField(
        	"template_name",
        	vocabulary_factory = "python-scripts-viewlets-templates",
        	schemata = "Listing",
            required = False,
        	widget = atapi.SelectionWidget(
                format='select',
            	label=_(u"Template"),
            	description=_(u"Template to use to render list of results"),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ The list of fields """
        # Return the 'inherit_viewlet_settings' field only if it's possible to inherit
        if any([i.get(self.context, inherit=True) for i in self.fields]):
            return self.fields
        else:
            return self.fields[1:]

