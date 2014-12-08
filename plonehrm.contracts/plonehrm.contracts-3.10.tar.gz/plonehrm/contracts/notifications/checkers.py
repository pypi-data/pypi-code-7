import logging

from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from zope.i18n import translate

from Products.plonehrm import utils
from Products.plonehrm.interfaces import IContractAdapter
from Products.plonehrm import PloneHrmMessageFactory as _hrm

from plonehrm.contracts import ContractsMessageFactory as _
from plonehrm.contracts.config import FIXED_CONTRACT_NOTIFICATION_TEMPLATE_ID
from plonehrm.contracts.notifications.events import ContractEndingEvent
from plonehrm.contracts.notifications.events import FixedContractEndingEvent
from plonehrm.contracts.notifications.events import TrialPeriodEndingEvent

from plonehrm.notifications.emailer import HRMEmailer
from plonehrm.notifications.interfaces import INotified
from plonehrm.notifications.utils import get_employees_for_checking
from zope.event import notify

logger = logging.getLogger("plonehrm.contracts:")

EXPIRY_NOTIFICATION = u"plonehrm.contracts: Expiry notification"
# Note: if you fix the spelling error in the next line (wek -> week),
# you will have to write a migration step for existing notifications.
# The text is never shown to end users, so never mind.
EXPIRY_NOTIFICATION_2 = u"plonehrm.contracts: Expiry notification (1 wek before)"
TRIAL_PERIOD_ENDING_NOTIFICATION = u"plonehrm.contracts: Trial period ending"
FIXED_CONTRACT_EXPIRY_NOTIFICATION_1 = u"plonehrm.contracts: Fixed contract expiry notification 1"
FIXED_CONTRACT_EXPIRY_NOTIFICATION_2 = u"plonehrm.contracts: Fixed contract expiry notification 2"


def find_correspondence(
        employee, contract, expires,
        correspondence_id=FIXED_CONTRACT_NOTIFICATION_TEMPLATE_ID):
    """Find correspondence object.

    Check if we already have a correspondence 'corresponding' with the
    template with the given correspondence_id.  By default we check
    for the template with the id that is meant for the notification
    about a fixed contract that is almost ending and is not going to
    be renewed.

    The tricky thing is that we might have created a correspondence
    for an earlier contract.  But if we have sent such a
    correspondence and have created a new contract anyway and that
    second contract is almost ending, then that is a bit weird.  Can
    happen.  We can check if there was such a correspondence during
    the contract duration.

    We mostly want yes/no, but let's return the found correspondence
    object or None.
    """
    start = contract.getStartdate()
    for brain in employee.getFolderContents(
            contentFilter={'portal_type': 'Correspondence'}):
        cor = brain.getObject()
        if getattr(cor, 'copied_from_template_id', '') != \
                correspondence_id:
            continue
        if start <= cor.date <= expires:
            logger.info("Found correspondence: %s", cor.absolute_url())
            return cor
    logger.info("Found NO correspondence for %s", employee.absolute_url())


def contract_ending_checker(object, event, now=None):
    """Check if the last contract of employees is almost ending.

    object is likely the portal, but try not to depend on that.

    'now' should not be specified, except for tests.
    """
    logger.info('Contract ending checker activated')

    portal = getToolByName(object, 'portal_url').getPortalObject()
    language_tool = getToolByName(portal, 'portal_languages')
    if language_tool:
        language = language_tool.getDefaultLanguage()
    else:
        language = 'en'

    employees = get_employees_for_checking(object)

    if now is None:
        now = DateTime()

    for brain in employees:
        try:
            employee = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
            continue

        # Get the last contract.  This may not be the current
        # contract, but can very well be a contract that starts a few
        # months in the future.
        contractAdapter = IContractAdapter(employee)
        last_contract = contractAdapter.get_last_contract()

        if last_contract is None:
            continue

        # Only fixed contracts can end.
        if not last_contract.getIsFixedDuration():
            continue
        # Get the expiry date.
        expires = last_contract.expiry_date()
        if expires is None:
            # Should only happen for non-fixed contracts, but we check
            # to be sure.
            continue

        addresses = utils.email_adresses_of_local_managers(employee)
        recipients = (addresses['worklocation_managers'] +
                      addresses['hrm_managers'] +
                      addresses['notified_persons'])

        if expires.isCurrentDay():
            # The last contract expired yesterday.
            link_text = translate(_hrm(u'title_go_to_employee',
                                       mapping={'name': employee.officialName()}),
                                  target_language=language)

            options = {'link_href': employee.absolute_url(),
                       'link_text': link_text}

            template = ZopeTwoPageTemplateFile('no_current_contract.pt')

            email = HRMEmailer(employee,
                               template=template,
                               options=options,
                               recipients=recipients,
                               subject=_(u'title_no_current_contract',
                                         default=u"${name}'s contract has ended",
                                         mapping={'name': employee.officialName()}))
            email.send()
            continue

        if expires < now:
            continue

        for days_warning, notification in [
                (31 * 2, FIXED_CONTRACT_EXPIRY_NOTIFICATION_1),
                (31 + 7, FIXED_CONTRACT_EXPIRY_NOTIFICATION_2)]:
            if now + days_warning < expires:
                continue
            # Check if we have already warned about this.
            notified = INotified(last_contract)
            if notified.has_notification(notification):
                continue
            # only if more than 6 months
            if last_contract.actual_duration() <= 6:
                continue
            # Check if we already have a 'corresponding'
            # correspondence.
            correspondence_id = FIXED_CONTRACT_NOTIFICATION_TEMPLATE_ID
            if find_correspondence(employee, last_contract, expires,
                                   correspondence_id):
                continue
            options = dict(days=days_warning)
            worklocation = aq_parent(employee)
            tool = worklocation.portal_correspondence
            if correspondence_id in tool.objectIds():
                correspondence = tool[correspondence_id]
                link_href = (employee.absolute_url() +
                             '/add_correspondence?template=' +
                             correspondence.UID())
            else:
                link_href = (
                    employee.absolute_url() + '/add_correspondence')
            link_text = _('Add notification letter')
            options['link_href'] = link_href
            options['link_text'] = link_text
            template = ZopeTwoPageTemplateFile(
                'fixed_contract_nears_ending.pt')
            email = HRMEmailer(employee,
                               template=template,
                               options=options,
                               recipients=recipients,
                               subject=_(u'title_fixed_contract_near_ending',
                                         default=u"${name}'s fixed contract is close to end.",
                                         mapping={'name': employee.officialName()}))
            email.send()
            notify(FixedContractEndingEvent(employee))
            notified.add_notification(notification)

        for days_warning, notification in [
                (31, EXPIRY_NOTIFICATION),
                (7, EXPIRY_NOTIFICATION_2)]:
            if now + days_warning >= expires:
                # Check if we have already warned about this.
                notified = INotified(last_contract)
                if notified.has_notification(notification):
                    continue
                # Check if we already have a correspondence about
                # ending the contract.
                correspondence_id = FIXED_CONTRACT_NOTIFICATION_TEMPLATE_ID
                if find_correspondence(employee, last_contract, expires,
                                       correspondence_id):
                    continue

                options = dict(days=days_warning)

                worklocation = aq_parent(employee)

                link_href = employee.absolute_url(
                ) + '/createObject?type_name='
                if worklocation.getCreateLetterWhenExpiry():
                    link_href += 'Letter'
                    link_text = _('Create a new letter')
                else:
                    link_href += 'Contract'
                    link_text = _('Create a new contract')

                options['link_href'] = link_href
                options['link_text'] = link_text
                if last_contract.actual_duration() <= 6:
                    options['deadline_day'] = True
                else:
                    options['deadline_month'] = True

                template = ZopeTwoPageTemplateFile('contract_nears_ending.pt')

                email = HRMEmailer(employee,
                                   template=template,
                                   options=options,
                                   recipients=recipients,
                                   subject=_(u'title_contract_near_ending',
                                             default=u"${name}'s contract is close to end.",
                                             mapping={'name': employee.officialName()}))
                email.send()
                notify(ContractEndingEvent(employee))
                notified.add_notification(notification)


def trial_period_ending_checker(object, event, now=None):
    """Check if the trial period of employees is almost ending.

    object is likely the portal, but try not to depend on that.

    now should only be specified in tests.
    """
    logger.info('Trying period ending checker activated')
    portal = getToolByName(object, 'portal_url').getPortalObject()
    days_warning = 7

    language_tool = getToolByName(portal, 'portal_languages')
    if language_tool:
        language = language_tool.getDefaultLanguage()
    else:
        language = 'en'

    toLocalizedTime = portal.restrictedTraverse('@@plone').toLocalizedTime

    employees = get_employees_for_checking(object)

    if now is None:
        now = DateTime()

    for brain in employees:
        try:
            employee = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
            continue

        contractAdapter = IContractAdapter(employee)
        current_contract = contractAdapter.current_contract(
            includeChangeLetters=False)

        if current_contract is None:
            continue
        trial_period_end = contractAdapter.trial_period_end()
        if trial_period_end is None:
            # for example when there is no trial period...
            continue

        if now + days_warning < trial_period_end:
            continue

        # Check if we have already warned about this.
        notified = INotified(current_contract)
        if notified.has_notification(TRIAL_PERIOD_ENDING_NOTIFICATION):
            continue

        link_text = translate(
            _hrm(u'title_go_to_employee',
                 mapping={'name': employee.officialName()}),
            target_language=language)

        options = {'date': toLocalizedTime(trial_period_end),
                   'link_href': employee.absolute_url(),
                   'link_text': link_text}
        template = ZopeTwoPageTemplateFile('trial_nears_ending.pt')

        addresses = utils.email_adresses_of_local_managers(employee)
        recipients = (addresses['worklocation_managers'] +
                      addresses['hrm_managers'] +
                      addresses['notified_persons'])
        email = HRMEmailer(
            employee,
            template=template,
            options=options,
            recipients=recipients,
            subject=_(u'title_trial_near_ending',
                      default=u"${name}'s trial period is close to end.",
                      mapping={'name': employee.officialName()}))
        email.send()

        notify(TrialPeriodEndingEvent(employee))
        notified.add_notification(TRIAL_PERIOD_ENDING_NOTIFICATION)
