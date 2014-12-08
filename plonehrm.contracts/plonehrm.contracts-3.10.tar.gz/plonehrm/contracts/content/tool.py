__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import registerType

from zope.i18n import translate
from zope.interface import implements

from plonehrm.contracts import config
from plonehrm.contracts.interfaces import IContractTool
from plonehrm.contracts import ContractsMessageFactory as _

from Products.plonehrm.tool import TemplateTool

schema = Schema((
    LinesField(
        name='functions',
        widget=LinesField._properties['widget'](
            label=_(u'contract_label_functions', default=u'Positions'),
        )
    ),
    LinesField(
        name='employmentTypes',
        widget=LinesField._properties['widget'](
            label=_(u'contract_label_employmentTypes',
                    default=u'Types of employment'),
        )
    ),
),
)

ContractTool_schema = BaseFolderSchema.copy() + schema.copy()


def custom_filter(context, templates):
    """ This method can be patched in sites using PloneHRM.

    It's goal is to add some more filterin on the templates returned
    by the listTemplates method of the ContractTool.
    context is the contract tool object. Templates is the
    default list returned by listTemplates.
    """
    return templates


class ContractTool(TemplateTool):
    """Contract tool.

      >>> from plonehrm.contracts.content.tool import ContractTool
      >>> tool = ContractTool()
      >>> tool.Title()
      'Contract templates'

      >>> tool.at_post_edit_script()

    """

    id = 'portal_contracts'
    security = ClassSecurityInfo()
    __implements__ = (BaseFolder.__implements__, )
    implements(IContractTool)

    typeDescription = "ContractTool"
    typeDescMsgId = 'description_edit_contracttool'

    schema = ContractTool_schema

    def __init__(self, *args, **kwargs):
        self.setTitle(translate(_(u'title_portal_contracts',
                                  default=u'Contract templates')))

    def listTemplates(self, type=None):
        templates = super(ContractTool, self).listTemplates(type)
        return custom_filter(self, templates)

registerType(ContractTool, config.PROJECTNAME)
