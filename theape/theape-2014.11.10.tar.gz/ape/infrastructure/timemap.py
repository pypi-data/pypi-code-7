
IN_PWEAVE = __name__ == '__builtin__'


# python standard library
import re
import math
from datetime import timedelta
from datetime import datetime
if IN_PWEAVE:
    import os

# third-party
from dateutil.relativedelta import relativedelta
import dateutil.parser
from validate import Validator

# this package
from ape import BaseClass
from ape import ApeError
from ape.parts.oatbran import CharacterClass, Numbers, Group
from ape.parts.oatbran import CommonPatterns
from ape.infrastructure.code_graphs import module_diagram, class_diagram


ZERO = '0'
INT_ZERO = 0
ONE = 1
MICRO = 10**6


class RelativeTimeMapGroups(object):
    __slots__ = ()
    years = 'years'
    months = 'months'
    weeks = 'weeks'
    days = 'days'
    hours = 'hours'
    minutes = 'minutes'
    seconds = 'seconds'
# end RelativeTimeMapGroups    


class RelativeTimeMap(BaseClass):
    """
    A converter from strings with relative times to seconds
    """
    def __init__(self):
        super(RelativeTimeMap, self).__init__()
        self._year_expression = None
        self._month_expression = None
        self._week_expression = None
        self._day_expression = None
        self._hour_expression = None
        self._minute_expression = None
        self._second_expression = None
        return

    @property
    def year_expression(self):
        """
        A compiled regex to match a year (only checks for y)
        """
        if self._year_expression is None:
            self._year_expression = re.compile(Group.named(name=RelativeTimeMapGroups.years,
                                                           expression=Numbers.real) +
                                                            CommonPatterns.optional_spaces +
                                                            CharacterClass.character_class('Yy')
                                                            )
        return self._year_expression

    @property
    def month_expression(self):
        """
        A compiled regex to match a month (check for 'mo' only)
        """
        if self._month_expression is None:
            self._month_expression = re.compile(Group.named(name=RelativeTimeMapGroups.months,
                                                            expression=Numbers.real) +
                CommonPatterns.optional_spaces +
                CharacterClass.character_class('Mm') +
                CharacterClass.character_class('Oo'))
        return self._month_expression

    @property
    def week_expression(self):
        """
        A compiled regex to extract a number of weeks
        """
        if self._week_expression is None:
            self._week_expression = re.compile(Group.named(name=RelativeTimeMapGroups.weeks,
                                                           expression=Numbers.real) +
                                                           CommonPatterns.optional_spaces +
                                                           CharacterClass.character_class('Ww'))
        return self._week_expression

    @property
    def day_expression(self):
        """
        A compiled regex to extract the number of days
        """
        if self._day_expression is None:
            self._day_expression = re.compile(Group.named(name=RelativeTimeMapGroups.days,
                                                          expression=Numbers.real) +
                                                          CommonPatterns.optional_spaces +
                                                          CharacterClass.character_class('Dd'))
        return self._day_expression

    @property
    def hour_expression(self):
        """
        A compiled regex to extract the number of hours
        """
        if self._hour_expression is None:
            self._hour_expression = re.compile(Group.named(name=RelativeTimeMapGroups.hours,
                                                           expression=Numbers.real) +
                                                           CommonPatterns.optional_spaces +
                                                           CharacterClass.character_class('Hh'))
        return self._hour_expression

    @property
    def minute_expression(self):
        """
        A compiled regex to extract the number of minutes
        """
        if self._minute_expression is None:
            self._minute_expression = re.compile(Group.named(name=RelativeTimeMapGroups.minutes,
                                                             expression=Numbers.real) +
                                                             CommonPatterns.optional_spaces +
                                                             CharacterClass.character_class('Mm') +
                                                             CharacterClass.character_class('Ii'))
        return self._minute_expression

    @property
    def second_expression(self):
        """
        A compiled regex to extract the number of seconds
        """
        if self._second_expression is None:
            self._second_expression = re.compile(Group.named(name=RelativeTimeMapGroups.seconds,
                                                             expression=Numbers.real) +
                                                             CommonPatterns.optional_spaces +
                                                             CharacterClass.character_class('Ss'))
        return self._second_expression
#end class RelativeTimeMap


def source_required(method):
    """
    Catches AttributeErrors and TypeErrors and raises ApeErrors in their place so the operators can recover

    :param:

      - `method`: the method to decorate
    """
    def wrapped(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (AttributeError, TypeError) as error:
            self.log_error(error)
            raise ApeError("self.source not set ('{0}')".format(self.source))
    return wrapped

def operation_error(method):
    """
    Catches AttributeErrors and TypeErrors and raises ApeErrors in their place so the operators can recover

    :param:

      - `method`: the method to decorate
      - `message`: for ApeError
    """
    def wrapped(self, other):
        try:
            return method(self, other)
        except TypeError as error:
            self.log_error(error)
            raise ApeError("operand must be timedelta object, not '{0}".format(other))
    return wrapped

def number_error(method):
    """
    Catches AttributeErrors and TypeErrors and raises ApeErrors in their place so the operators can recover

    :param:

      - `method`: the method to decorate
    """
    def wrapped(self, other):
        try:
            return method(self, other)
        except TypeError as error:
            self.log_error(error)
            raise ApeError("operand must be numeric object, not '{0}".format(other))
    return wrapped

def unary_error(method):
    """
    Catches AttributeErrors and TypeErrors and raises ApeErrors in their place so the operators can recover

    :param:

      - `method`: the method to decorate
    """
    def wrapped(self):
        try:
            return method(self)
        except TypeError as error:
            self.log_error(error)
            raise ApeError("timedelta must be object, not '{0}".format(self.timedelta))
    return wrapped




class RelativeTime(BaseClass):
    """
    A timedeltas extension
    """
    def __init__(self, source=None):
        """
        RelativeTime constructor

        :param:

         - `source`: A string with relative time in it (e.g. '1week 2 days 4.2 seconds')
        """
        super(RelativeTime, self).__init__()
        self.timedelta = None
        self._time_map = None
        self._source = None
        self.source = source    
        return

    @property
    def source(self):
        """
        :return: the source string
        """
        return self._source

    @source.setter
    def source(self, source):
        """
        sets the source and all the time values (if source is None, resets the values)
        """
        self._source = source
        if source is not None:            
            self.populate_fields()
        else:
            self.reset()
        return
    
    @property
    def time_map(self):
        """
        A relative time map instance to parse the source.
        """
        if self._time_map is None:
            self._time_map = RelativeTimeMap()
        return self._time_map

    @property
    @source_required
    def days(self):
        """
        gets the timedelta days

        :return: number of days as an integer
        :raise: ApeError if the timedelta hasn't been built
        """
        return self.timedelta.days
    
    @property
    @source_required
    def seconds(self):
        """
        Gets the seconds from the time-delta

        :return: seconds (not total-seconds) as integer
        :raise: ApeError if the timedelta hasn't been built
        """
        return self.timedelta.seconds

    @property
    @source_required
    def microseconds(self):
        """
        Gets the microseconds from the timedelta

        :return: seconds (not total-seconds) as an integer
        :raise: ApeError if the timedelta not built not set
        """
        return self.timedelta.microseconds

    @source_required
    def get_number(self, expression, group_name):
        """
        gets the number from self.source that matches the expression

        :return: string with number or '0' if not found
        :raise: ApeError if self._source has not been set or group is missing
        :raise: IndexError if the group_name is not found (this is likely an implementation error, we want to crash)
        """
        match = expression.search(self.source)
        if match is None:
            return '0'
        return match.group(group_name)
   
    def populate_fields(self):
        """
        populates the time fields with values (e.g. self.minutes)

        """
        years = self.get_number(self.time_map.year_expression, RelativeTimeMapGroups.years)
        months = self.get_number(self.time_map.month_expression, RelativeTimeMapGroups.months)
        weeks = self.get_number(self.time_map.week_expression, RelativeTimeMapGroups.weeks)
        days = self.get_number(self.time_map.day_expression, RelativeTimeMapGroups.days)
        hours = self.get_number(self.time_map.hour_expression, RelativeTimeMapGroups.hours)
        minutes = self.get_number(self.time_map.minute_expression, RelativeTimeMapGroups.minutes)
        seconds = self.get_number(self.time_map.second_expression, RelativeTimeMapGroups.seconds)

        now = datetime.now()

        # HACK
        # timedelta doesn't handle varying-units (e.g. 28 vs 30 vs 31 day in a month)
        # relativedelta does -- but it returns a datetime object, not a timedelta
        # so the adding and subtracting is to convert it to a timedelta
        self.timedelta = now + relativedelta(years=int(years),
                                             months=int(months),
                                             weeks=float(weeks),
                                             days=float(days),
                                             hours=float(hours),
                                             minutes=float(minutes),
                                             seconds=float(seconds)) - now
        
        return

    @source_required
    def total_seconds(self):
        """
        gets the timedelta total_seconds

        :return: all the times summed to seconds (as a float)
        :raise: ApeError if the source has not been set
        """
        return self.timedelta.total_seconds()

    def reset(self):
        """
        Resets the attributes (undoes populate_fields)
        """
        self.timedelta = None
        return

    # the operator overloading
    def __eq__(self, other):
        """
        Checks if the timedelta is the same as the other.

        :param:

         - `other`: timedelta

        :return: True if self.timedelta is equal to other
        """
        return self.timedelta == other

    def __lt__(self, other):
        """
        Checks if the timedelta is less than the other
        """
        return self.timedelta < other

    def __gt__(self, other):
        """
        Checks if the timedelta is > other        
        """
        return self.timedelta > other
    
    def __le__(self, other):
        """
        Checks if the timedelta is <= other
        """
        return self.timedelta <= other

    def __ge__(self, other):
        """
        Checks if the timedelta is >= other
        """
        return self.timedelta >= other

    def __ne__(self, other):
        """
        Checks to see if the timedelta isn't equal to the other

        :return: True if they aren't equal
        """
        return self.timedelta != other
    
    def __cmp__(self, other):
        """
        Compares timestamp with other timestamp

        :param:

         - `other`: a timedelta

        :return: -1 if less, 0 if equal, 1 if greater
        """
        if self.timedelta == other:
            return 0
        if self.timedelta < other:
            return -1
        if self.timedelta > other:
            return 1
        return
    
    @operation_error
    def __add__(self, other):
        """
        adds the timedelta to other

        :param:

         - `other`: a timedelta object

        :return: self.timedelta + other
        """
        return self.timedelta + other

    @operation_error
    def __radd__(self, other):
        """
        adds the timedelta to other

        :param:

         - `other`: a timedelta object

        :return: self.timedelta + other
        """
        return self.timedelta + other

    @operation_error
    def __sub__(self, other):
        """
        subtracts the other from the timedelta

        :param:

         - `other`: a timedelta object

        :return: self.timedelta - other
        """
        return self.timedelta - other

    @operation_error
    def __rsub__(self, other):
        """
        subtracts the timedelta from the other

        :param:

         - `other`: a timedelta object

        :return: other - self.timedelta
        """
        return other - self.timedelta

    @number_error
    def __mul__(self, multiplier):
        """
        mulitplies the timedelta

        :return: timedelta * multiplier        
        """
        return self.timedelta * multiplier

    @number_error
    def __rmul__(self, multiplier):
        """
        mulitplies the timedelta

        :return: multiplier * timedelta        
        """
        return multiplier * self.timedelta

    def __str__(self):
        """
        Pass-through to the time-delta
        """
        return str(self.timedelta)

    def __repr__(self):
        """
        Pass-through to the timedelta
        """
        return self.timedelta.__repr__()

    @unary_error
    def __neg__(self):
        """
        Negates the timedelta

        :return: -self.timedelta
        """
        return -self.timedelta

    @unary_error
    def __pos__(self):
        """
        Makes the timedelta positive

        :return: +self.timedelta
        """
        return +self.timedelta

    @unary_error
    def __abs__(self):
        """
        Calls the absolute function on the timedelta

        :return: abs(self.timedelta)
        """
        return abs(self.timedelta)

    @number_error
    def __floordiv__(self, integer):
        """
        Computes the floor and throws away the remainder

        :return: self.timedelta // integer        
        """
        return self.timedelta // integer

    def __str__(self):
        return self.source
# end class RelativeTime    


class AbsoluteTime(BaseClass):
    """
    A container for the dateutil.parser.parse
    """
    def __init__(self, default=None, ignoretz=False, tzinfos=None, dayfirst=False,
                 yearfirst=False, fuzzy=True, parserinfo=None):
        """
        AbsoluteTime constructor

        :param:

         - `default`: datetime object to use to supply missing fields
         - `ignoretz`: if true, ignore timezone information in string
         - `tzinfos`: dict or function that provides custom timezone information
         - `dayfirst`: if true, ambiguous dates assume DD-MM-YY first
         - `yearfirst`: if true, ambiguous dates assume YY-MM-DD
         - `fuzzy`: if true, ignore unrecognizable tokens
         - `parserinfo`: parserinfo class that changes the behavior of the parser
        """
        super(AbsoluteTime, self).__init__()
        self.default = default
        self.ignoretz = ignoretz
        self.tzinfos = tzinfos        
        self.dayfirst = dayfirst
        self.yearfirst = yearfirst
        self.fuzzy = fuzzy
        self.parserinfo = parserinfo
        return

    def __call__(self, source):
        """
        The main interface -- calls dateutil.parser.parse(source)

        :param:

         - `source`: string with time and date information to create datetime

        :return: datetime object created from `source`
        :raise: ApeError if the string is unrecognizable
        """
        try:
            return dateutil.parser.parse(source,
                                         default=self.default,
                                         ignoretz=self.ignoretz,
                                         tzinfos=self.tzinfos,
                                         dayfirst=self.dayfirst,
                                         yearfirst=self.yearfirst,
                                         fuzzy=self.fuzzy,
                                         parserinfo=self.parserinfo)
        except ValueError as error:
            self.log_error(error)
            raise ApeError("dateutil.parser.parse unable to parse '{0}'".format(source))
        return
# end class AbsoluteTime            


time_validator = Validator({'relative_time':RelativeTime,
                       'absolute_time':AbsoluteTime()})


if __name__ == '__main__':
    import pudb; pudb.set_trace()
    r = RelativeTime('3 seconds')
    t = timedelta(seconds=3)
    r.seconds
    check = r != t
