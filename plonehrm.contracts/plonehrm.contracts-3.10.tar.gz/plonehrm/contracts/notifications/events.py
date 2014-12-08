from zope.i18n import translate
from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName

from Products.plonehrm.interfaces import IContractAdapter

from plonehrm.contracts import ContractsMessageFactory as _
from plonehrm.contracts.config import FIXED_CONTRACT_NOTIFICATION_TEMPLATE_ID
from plonehrm.contracts.notifications.interfaces import IContractEvent


class NoContractEvent(ObjectEvent):
    implements(IContractEvent)


class ContractEndingEvent(ObjectEvent):
    """Contract is almost ending.
    """
    implements(IContractEvent)

    # This needs to be handled by a (HRM) Manager, e.g. a checklist
    # item specifically for managers needs to be created.
    for_manager = True

    def __init__(self, *args, **kwargs):
        super(ContractEndingEvent, self).__init__(*args, **kwargs)

        # We get the settings of the worklocaton to see
        # if a new letter or a new contract shall be created.
        worklocation = aq_parent(self.object)

        if worklocation.getCreateLetterWhenExpiry():
            new_type = 'Letter'
            text = _('msg_make_new_letter', u"Make new letter")
        else:
            new_type = 'Contract'
            text = _('msg_make_new_contract', u"Make new contract")

        create_url = self.object.absolute_url() + \
            '/createObject?type_name=' + new_type

        # Get the expiry date.
        contractAdapter = IContractAdapter(self.object)
        last_contract = contractAdapter.get_last_contract()
        if not last_contract:
            # Should not happen.
            expires = None
        else:
            expires = last_contract.expiry_date()

        # Add a message to make a new contract, with the correct link.
        props = getToolByName(self.object, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')
        text = translate(text, target_language=lang)

        self.message = text
        self.link_url = create_url
        self.date = expires


class FixedContractEndingEvent(ObjectEvent):
    """Fixed contract is almost ending.
    """
    implements(IContractEvent)

    # This needs to be handled by a (HRM) Manager, e.g. a checklist
    # item specifically for managers needs to be created.
    for_manager = True

    def __init__(self, *args, **kwargs):
        super(FixedContractEndingEvent, self).__init__(*args, **kwargs)

        # We get the settings of the worklocaton to see
        # if a new letter or a new contract shall be created.
        worklocation = aq_parent(self.object)
        tool = worklocation.portal_correspondence
        correspondence_id = FIXED_CONTRACT_NOTIFICATION_TEMPLATE_ID
        if correspondence_id in tool.objectIds():
            correspondence = tool[correspondence_id]
            create_url = (self.object.absolute_url() +
                          '/add_correspondence?template=' +
                          correspondence.UID())
        else:
            create_url = (
                self.object.absolute_url() + '/add_correspondence')
        text = _('Add notification letter about end of contract.')

        # Get the expiry date.
        contractAdapter = IContractAdapter(self.object)
        last_contract = contractAdapter.get_last_contract()
        if not last_contract:
            # Should not happen.
            expires = None
        else:
            expires = last_contract.expiry_date() - 31

        # Add a message to notify about the end of the contract, with
        # the correct link.
        props = getToolByName(self.object, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')
        text = translate(text, target_language=lang)

        self.message = text
        self.link_url = create_url
        self.date = expires


class TrialPeriodEndingEvent(ObjectEvent):
    """Trial period is almost ending.
    """
    implements(IContractEvent)

    # This needs to be handled by a (HRM) Manager, e.g. a checklist
    # item specifically for managers needs to be created.
    for_manager = True

    def __init__(self, *args, **kwargs):
        super(TrialPeriodEndingEvent, self).__init__(*args, **kwargs)
        trial_period_end = IContractAdapter(self.object).trial_period_end()

        # Add a warning message.
        toLocalizedTime = self.object.restrictedTraverse(
            '@@plone').toLocalizedTime
        trial_period_end = toLocalizedTime(trial_period_end)
        text = _(u"Trial period ends at ${date}.",
                 mapping=dict(date=trial_period_end))
        props = getToolByName(self.object, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')
        self.message = translate(text, target_language=lang)
