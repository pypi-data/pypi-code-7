__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from Products.Archetypes.atapi import registerType
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import DisplayList
from Products.CMFCore.utils import getToolByName

from Products.plonehrm.interfaces import IContractAdapter, ITemplatedObject

from plonehrm.contracts import config
from plonehrm.contracts.content.contract import Contract
from plonehrm.contracts.content.contract import Contract_schema
from plonehrm.contracts.interfaces import ILetter

Letter_schema = Contract_schema.copy()
Letter_schema['trialPeriod'].widget.visible = {'view': 'visible',
                                               'edit': 'invisible'}
Letter_schema['isFixedDuration'].default = False
Letter_schema['isFixedDuration'].widget.visible = {'view': 'visible',
                                                   'edit': 'invisible'}
Letter_schema['duration'].widget.visible = {'view': 'visible',
                                            'edit': 'invisible'}
Letter_schema['expirydate'].widget.visible = {'view': 'visible',
                                              'edit': 'invisible'}


class Letter(Contract):
    """Letter for change of contract
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(Contract, '__implements__', ()), )
    implements(ILetter, ITemplatedObject, )

    _at_rename_after_creation = True

    schema = Letter_schema

    security.declarePrivate('_templates')

    def _templates(self):
        """Vocabulary for the template field
        """
        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None:
            return []
        else:
            items = [(item.id, item.Title()) for item
                     in tool.listTemplates('letter')]
            return DisplayList(items)

    def is_contract(self):
        return False

    def _get_value_from_contract(self, name, default=None):
        employee = self.get_employee()
        if not employee:
            return default

        contractAdapter = IContractAdapter(employee)
        contract = contractAdapter.contract_of_letter(self)
        if contract:
            value = getattr(contract, name, default)
            if callable(value):
                value = value()
            return value

        return default

    def getIsFixedDuration(self):
        """Does this letter have a fixed duration?

        The isFixedDuration field only makes sense for contracts, but
        we had it enabled for change letters too.  Change letters are
        supposed to automatically end when their contract ends or when
        a new change letter is made.

        We could return the value of the matching contract, but that
        is where getContractIsFixedDuration is for.
        """
        return False

    def getDuration(self):
        # Ignore the duration field.
        return None

    def getExpirydate(self):
        # Ignore the explicit expirydate field.  Note that calling
        # self._get_value_from_contract('getExpirydate') will not
        # work, because you end up in an infinite loop then.
        return None

    def getContractIsFixedDuration(self):
        # Get isFixedDuration from contract.
        return self._get_value_from_contract('getIsFixedDuration', False)

    def getContractDuration(self):
        # Get duration from contract.
        return self._get_value_from_contract('getDuration')

    def getContractExpirydate(self):
        # Get expiry date from contract.
        return self._get_value_from_contract('getExpirydate')

    def expiry_date(self, default=None):
        """ Works like expiry date for contract.
        The main difference is that we check if the letter is defined inside
        a contract if we can not define the end date.
        """
        expires = super(Letter, self).expiry_date(default)

        employee = self.get_employee()
        if not employee:
            return expires

        contractAdapter = IContractAdapter(employee)
        contract = contractAdapter.contract_of_letter(self)

        if not contract:
            return expires

        contract_expires = contract.expiry_date()
        if not contract_expires:
            return expires

        if contract_expires < expires or not expires:
            return contract_expires

        return expires


registerType(Letter, config.PROJECTNAME)
