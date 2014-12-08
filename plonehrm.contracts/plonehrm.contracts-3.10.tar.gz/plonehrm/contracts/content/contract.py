__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Acquisition import aq_chain, aq_inner, aq_parent
from DateTime import DateTime
from datetime import datetime, date

from Products.Archetypes.utils import IntDisplayList
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.atapi import BaseContent
from Products.Archetypes.atapi import BaseSchema
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import DecimalWidget
from Products.Archetypes.atapi import IntegerWidget
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import FixedPointField
from Products.Archetypes.atapi import FloatField
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import registerType

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.plonehrm.interfaces import IEmployee, IWorkLocation, ITemplatedObject
from Products.plonehrm.utils import is_expiry_date_within_range, actual_contract_duration
from zope.interface import implements
from zope.i18n import translate
from persistent import Persistent

from Products.plonehrm.interfaces import IContractAdapter
from Products.plonehrm.content.plonehrm_document import PloneHRMDocument

from plonehrm.contracts import config
from plonehrm.contracts.interfaces import IContract
from plonehrm.contracts import ContractsMessageFactory as _

schema = Schema((
    StringField(name='template',
                required=1,
                vocabulary='_templates',
                read_permission='plonehrm: View hrm content',
                write_permission='plonehrm: Modify contract',
                widget=SelectionWidget(
                    format='select',
                    condition='not:object/is_signed',
                    visible={'view': 'visible', 'edit': 'invisible'},
                    label=_(u'contract_label_template', default=u'Template'),
                ),
                ),
    FixedPointField(
        name='wage',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        validators=('isCurrency', ),
        default_method='default_wage',
        widget=DecimalWidget(
            condition='not:object/is_signed',
            label=_(u'contract_label_wage', default=u'Wage'),
        ),
        schemata='Values',
    ),

    StringField(
        name='function',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        default_method='default_function',
        widget=SelectionWidget(
            format='select',
            condition='not:object/is_signed',
            label=_(u'contract_label_function', default=u'Function'),
        ),
        vocabulary='_available_functions',
        schemata='Values',
    ),

    DateTimeField(
        name='startdate',
        required=True,
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=CalendarWidget(
            condition='not:object/is_signed',
            show_hm=0,
            label=_(u'contract_label_startdate', default=u'Start date'),
        ),
        schemata='Values',
    ),
    BooleanField(
        name='isFixedDuration',
        default=True,
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=BooleanWidget(
            condition='not:object/is_signed',
            label=_(u'contract_label_is_fixed_duration',
                    default=u'Fixed duration'),
        ),
        schemata='Values',
    ),
    IntegerField(
        name='duration',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=IntegerWidget(
            condition='not:object/is_signed',
            label=_(u'contract_label_duration', default=u'Duration (months)'),
        ),
        schemata='Values',
    ),
    DateTimeField(
        name='expirydate',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        widget=CalendarWidget(
            condition='not:object/is_signed',
            show_hm=0,
            label=_(
                u'contract_label_expirydate',
                default=u'Explicit expiry date'),
        ),
        schemata='Values',
    ),
    IntegerField(
        name='trialPeriod',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        default=0,
        widget=SelectionWidget(
            format='select',
            condition='not:object/is_signed',
            label=_(u'contract_label_trial_period',
                    default=u'Trial period (months)'),
        ),
        vocabulary='_trial_period_vocabulary',
        schemata='Values',
    ),
    StringField(
        name='employmentType',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        default_method='default_employment_type',
        widget=SelectionWidget(
            condition='not:object/is_signed',
            format='select',
            label=_(u'contract_label_employmentType',
                    default=u'Type of employment'),

        ),
        vocabulary='_available_employment_types',
        schemata='Values',
    ),
    FloatField(
        name='hours',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        default_method='default_hours',
        widget=DecimalWidget(
            condition='not:object/is_signed',
            label=_(u'contract_label_hours', default=u'Number of hours'),
        ),
        schemata='Values',
    ),
    FloatField(
        name='daysPerWeek',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify contract',
        default_method='default_days_per_week',
        validators=('maxDaysPerWeek', ),
        widget=DecimalWidget(
            condition='not:object/is_signed',
            label=_(u'contract_label_days_per_week',
                    default=u'Number of workdays per week'),
        ),
        schemata='Values',
    ),
    TextField(name='text',
              required=False,
              seachable=False,
              primary=True,
              default_output_type='text/x-html-safe',
              widget=RichWidget(
                  description='',
                  label=_(u'label_body_text', default=u'Body Text'),
                  rows=25,
                  visible={'view': 'visible', 'edit': 'visible'},
              ),
              )
),
)

Contract_schema = BaseSchema.copy() + schema.copy()
# We take the title of the chosen template usually, but this can be
# overridden by specifically filling in a title.  But at least the
# title is now not required:
Contract_schema['title'].required = False
Contract_schema['title'].widget.visible = {'view': 'visible',
                                           'edit': 'invisible'}

for schema_key in Contract_schema.keys():
    if Contract_schema[schema_key].schemata in ['metadata',
                                                'categorization']:
        Contract_schema[schema_key].widget.visible = {'edit': 'invisible',
                                                      'view': 'invisible'}


class ContractHourSpread(Persistent):
    def __init__(self):
        # Mode can be manual, manual_oddeven or auto.
        self.mode = 'auto'

        # Number of hours worked by week.
        self.total_hours = 0

        # Stores the number of hours per day.
        # Each cell is referenced as week_type + '_' + day number.
        # For example, 'even_0' defines number of hours worked on
        # monday of even weeks. 'odd_3' defines number of jours
        # worked on thurday for odd weeks.
        self.hours = {}
        for week in ['odd', 'even']:
            for day in range(0, 7):
                self.hours[week + '_' + str(day)] = 0

    def getHoursForWeek(self, week):
        total = 0.0

        for day in range(0, 7):
            total += self.hours[week + '_' + str(day)]

        return total


class Contract(BaseContent, PloneHRMDocument):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (BaseContent.__implements__, )
    implements(IBaseContent, IContract, ITemplatedObject, )
    _at_rename_after_creation = True

    schema = Contract_schema

    def getWage(self):
        """Override the default getting to return a comma in some cases.

        We just look at the default language and check if it is in a
        list of languages that we know use commas in their currencies.
        """

        wage = self.getField('wage').get(self)
        language_tool = getToolByName(self, 'portal_languages')
        if language_tool:
            language = language_tool.getDefaultLanguage()
        else:
            language = 'en'
        if language in ('nl', 'de', 'fr'):
            wage = wage.replace('.', ',')
        return wage

    security.declarePrivate('_templates')

    def _templates(self):
        """Vocabulary for the template field
        """
        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None:
            return []
        else:
            items = [(item.id, item.Title()) for item
                     in tool.listTemplates('contract')]
            return DisplayList(items)

    security.declarePublic('template_chosen')

    def template_chosen(self):
        """Determine if the template (a string) has been chosen yet.
        """
        return len(self.getTemplate()) > 0

    security.declarePrivate('_available_functions')

    def _available_functions(self):
        """Vocabulary for the functions field
        """
        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None:
            return []
        else:
            return tool.getFunctions()

    security.declarePrivate('_available_employment_types')

    def _available_employment_types(self):
        """Vocabulary for the employmentType field
        """
        tool = getToolByName(self, 'portal_contracts', None)
        if tool is None:
            return []
        else:
            return tool.getEmploymentTypes()

    security.declarePrivate('_trial_period_vocabulary')

    def _trial_period_vocabulary(self):
        """Vocabulary for the trialPeriod field
        """
        return IntDisplayList([(0, '0'), (1, '1'), (2, '2')])

    security.declareProtected(permissions.View, 'post_validate')

    def post_validate(self, REQUEST=None, errors=None):
        # So validation of fields that need to be checked together,
        # especially start and expiry date.
        if REQUEST is None:
            return
        if errors is None:
            errors = {}
        if 'startdate' in errors or 'expirydate' in errors:
            # No need to do extra checking.
            return
        form = REQUEST.form
        if 'expirydate' not in form:
            return
        expirydate = form['expirydate']
        if not expirydate:
            # It is optional
            return
        # If isFixedDuration is False we need not care about any of this.
        if not form.get('isFixedDuration', self.getIsFixedDuration()):
            return

        # Check if expiry date is not before start date.
        startdate = form['startdate']
        if expirydate <= startdate:
            error = _(u'msg_error_incorrect_enddate',
                      default=u'The end date must be after the start date.')
            error = translate(error, context=REQUEST)
            errors['expirydate'] = error
            return error

        # Check if expirydate is not too far from start date plus duration.
        if 'duration' in errors:
            # Nothing more to check.
            return
        duration = form.get('duration', self.getDuration())
        duration = int(duration)
        startdate = DateTime(startdate)
        expirydate = DateTime(expirydate)
        if not is_expiry_date_within_range(startdate, expirydate, duration):
            error = _(u'msg_error_incorrect_enddate_for_duration',
                      default=u'The end date differs too much from the start '
                              u'date plus the duration.')
            error = translate(error, context=REQUEST)
            errors['expirydate'] = error
            return error

    def get_employee(self):
        """Get the employee that this contract is in.

        Note that we probably are in the portal_factory, so our direct
        parent is not an Employee.  But we can traverse up the
        acquisition chain to find it.
        """
        for parent in aq_chain(aq_inner(self)):
            if IEmployee.providedBy(parent):
                return parent

    def get_worklocation(self):
        """Get the worklocation that this contract is in.
        """
        for parent in aq_chain(aq_inner(aq_parent(self))):
            if IWorkLocation.providedBy(parent):
                return parent

    def base_contract(self):
        """Get the current contract of the parent Employee.
        """
        parent = self.get_employee()
        if parent is None:
            return
        contractAdapter = IContractAdapter(parent)
        return contractAdapter.current_contract()

    def default_wage(self):
        """Get the wage of the parent Employee.
        """
        base = self.base_contract()
        if base is None or base == self:
            return '0.00'
        return base.getWage()

    def default_function(self):
        """Get the function of the parent Employee.
        """
        base = self.base_contract()
        if base is None or base == self:
            return ''
        return base.getFunction()

    def default_hours(self):
        """Get the hours of the parent Employee.
        """
        base = self.base_contract()
        if base is None or base == self:
            return ''
        return base.getHours()

    def default_employment_type(self):
        """Get the employment type of the parent Employee.
        """
        base = self.base_contract()
        if base is None or base == self:
            return ''
        return base.getEmploymentType()

    def default_days_per_week(self):
        """Get the days per week of the parent Employee.
        """
        base = self.base_contract()
        if base is None or base == self:
            return 0
        return base.getDaysPerWeek()

    def _expiry_date(self):
        """ Computes the default expiry date.
        """
        expiry = self.getExpirydate()
        if expiry is not None:
            # The expiry date has been set explicitly.
            return expiry
        start = self.getStartdate()
        duration = self.getDuration()
        if start is None or duration is None:
            return None

        year, month, day = start.year(), start.month(), start.day()
        year = year + (month + duration - 1) / 12
        month = 1 + (month + duration - 1) % 12
        first_of_month = DateTime(year, month, 1)
        mydate = first_of_month + day - 1
        # 31 January + 31 days is 3 March, so count backwards in that
        # case.  Watch out for infinite loops here...
        safety_count = 5
        while mydate.month() != month and safety_count > 0:
            safety_count -= 1
            mydate -= 1
        if not safety_count:
            return None

        return mydate - 1

    def expiry_date(self, default=None):
        """Expiry date of this contract.

        Basically start date + duration.  But e.g. a contract of one
        month starting at 31 January should end at 28 (or 29) February.

        Will return None if start date or duration is not known.

        If we have an explicit expiry date, we show that.
        """

        if self.getIsFixedDuration():
            return self._expiry_date()

        # We have a contract without an end date, so it never expires.
        # We check if the employee still works.
        parent = self.get_employee()
        if parent is None:
            return

        contractAdapter = IContractAdapter(parent)
        end_date = contractAdapter.getEndEmploymentDate()

        if end_date:
            return end_date

        if default:
            if isinstance(default, datetime) or isinstance(default, date):
                default = DateTime(default.year,
                                   default.month,
                                   default.day)

            return default
        return None

    def getHoursForWeek(self, week):
        contractAdapter = IContractAdapter(self.get_employee())
        schedule = contractAdapter.get_working_schedule(
            contract=self)

        return schedule.getHoursForWeek(week)

    def getHoursPerWeek(self):
        odd = self.getHoursForWeek('odd')
        even = self.getHoursForWeek('even')

        return (odd + even) / 2.0

    def is_contract(self):
        return True

    def getPercentage(self):
        wl = self.get_worklocation()
        try:
            wl_hours = float(wl.getDefaultHoursPerWeek())
        except:
            wl_hours = 0.0

        if wl_hours == 0:
            wl_hours = 40.0

        contract_hours = self.getHoursPerWeek()
        if not contract_hours:
            contract_hours = 0.0

        return round((contract_hours * 100) / wl_hours, 2)

    def after_sign_redirect(self):
        return self.get_employee().absolute_url() + '/contract_history'

    def getContractIsFixedDuration(self):
        return self.getIsFixedDuration()

    def getContractDuration(self):
        return self.getDuration()

    def getContractExpirydate(self):
        return self.getExpirydate()

    def actual_duration(self):
        """Actual duration of contract in months for fixed contract.

        Note that you should not use this to compare the duration of
        two contracts.  That is just too weird with months in various
        sizes.

        Due to an explicit expiry date it may be slightly less or more
        than the duration in months.  And you cannot use the
        difference in days and divide by 30 to get the number of
        months.  For several calculations we need to know whether a
        duration is exactly x months or slightly more or less.

        Most of the doc tests are now done in the
        actual_contract_duration function, but let's keep a few.

        We need to setup a bit of zcml in these unit tests:

        >>> from Products.Archetypes.Schema.factory import instanceSchemaFactory
        >>> from zope.component import provideAdapter
        >>> provideAdapter(instanceSchemaFactory)

        Now the tests.

        >>> contract = Contract('id')
        >>> contract.actual_duration()
        0.0
        >>> contract.getIsFixedDuration()
        True
        >>> contract.setIsFixedDuration(False)
        >>> contract.actual_duration()
        0.0
        >>> contract.setDuration(6)
        >>> contract.actual_duration()
        0.0
        >>> contract.setIsFixedDuration(True)
        >>> contract.setStartdate(DateTime(2010, 1, 1))
        >>> contract.actual_duration()
        6.0

        With expiry dates, unfortunately we always get rounding
        errors, which are totally not interesting.  So we use a
        helper function.

        >>> def almost_equal(a, b):
        ...     return abs(a - b) < 0.01
        >>> almost_equal(1, 2)
        False
        >>> almost_equal(1, 1)
        True
        >>> almost_equal(1, 1.01)
        False
        >>> almost_equal(1, 1.009)
        True
        >>> almost_equal(1, 0.99)
        False
        >>> almost_equal(1, 0.991)
        True

        1 January with a duration of seven months means an expiry date
        of 31 July.  Setting that date explicitly should not influence
        the calculation.  Having a day more or less should.

        >>> contract.setExpirydate(DateTime(2010, 7, 31))
        >>> duration = contract.actual_duration()
        >>> almost_equal(duration, 7.0) or duration
        True
        >>> contract.setExpirydate(DateTime(2010, 7, 30))
        >>> duration = contract.actual_duration()
        >>> almost_equal(duration, 6.97) or duration
        True
        >>> contract.setExpirydate(DateTime(2010, 8, 1))
        >>> duration = contract.actual_duration()
        >>> almost_equal(duration, 7.03) or duration
        True

        The end of the month is tricky.  Take the end of February.

        >>> contract.setStartdate(DateTime(2010, 2, 28))
        >>> contract.setExpirydate(DateTime(2010, 3, 27))
        >>> duration = contract.actual_duration()
        >>> almost_equal(duration, 0.90) or duration
        True
        >>> contract.setExpirydate(DateTime(2010, 3, 28))
        >>> duration = contract.actual_duration()
        >>> almost_equal(duration, 0.94) or duration
        True
        >>> contract.setExpirydate(DateTime(2010, 3, 29))
        >>> duration = contract.actual_duration()
        >>> almost_equal(duration, 0.97) or duration
        True
        >>> contract.setExpirydate(DateTime(2010, 3, 30))
        >>> duration = contract.actual_duration()
        >>> almost_equal(duration, 1.0) or duration
        True
        >>> contract.setExpirydate(DateTime(2010, 3, 31))
        >>> duration = contract.actual_duration()
        >>> 1.02 < duration < 1.07 or duration
        True

        """
        if not self.getIsFixedDuration():
            return 0.0
        duration = self.getDuration()
        startdate = self.getStartdate()
        expirydate = self.getExpirydate()
        return actual_contract_duration(
            duration=duration, startdate=startdate, expirydate=expirydate)


registerType(Contract, config.PROJECTNAME)
