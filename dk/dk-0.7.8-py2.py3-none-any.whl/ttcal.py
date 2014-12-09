# -*- coding: utf-8 -*-

"""Date classes (originally from TikTok).
"""

# pylint:disable=W0141,R0904
# W0141 using function `map`.
# R0904: too many public methods.

import six
import re
import datetime, calendar
from itertools import islice
from .fstr import fstr


def chop(it, n):
    "Chop iterator into `n` size chuchks."
    while 1:
        s = list(islice(it, n))
        if not s:
            break
        yield s


class RangeMixin(object):
    """Requires other class to define .first and .last attributes.
    """
    def range(self):
        "Return an iterator for the range of `self`."
        if hasattr(self, 'dayiter'):
            return self.dayiter()
        return Days(self.first, self.last)
    
    def between_tuple(period):  # pylint:disable=E0213
        """Return a tuple of datetimes that is convenient for sql
           `between` queries.
        """
        return (period.first.datetime(),
                (period.last + 1).datetime() - datetime.timedelta(seconds=1))

    @property
    def middle(self):
        """Return the day that splits the date range in half.
        """
        middle = (self.first.toordinal() + self.last.toordinal()) // 2
        return Day.fromordinal(middle)


class CompareMixin(object):  # pylint:disable=R0903
    """Mixin class that defines comparison operators, by comparing the
       (year, month, day) tuple returned by ``datetuple()``.
       This makes Year() <= Month() <= Week() <= Today().
    """
    def timetuple(self):
        """Create timetuple from datetuple.
           (to interact with datetime objects).
        """
        d = datetime.date(*self.datetuple())
        t = datetime.time()
        return datetime.datetime.combine(d, t)

    def __le__(self, other):
        try:
            return self.timetuple() <= other.timetuple()
        except:
            return False
    
    def __lt__(self, other):
        try:
            return self.timetuple() < other.timetuple()
        except:
            return False
    
    def __eq__(self, other):
        try:
            return self.timetuple() == other.timetuple()
        except:
            return False

    def __ne__(self, other):
        try:
            return not (self == other)
        except:
            return True

    def __gt__(self, other):
        try:
            return self.timetuple() > other.timetuple()
        except:
            return False

    def __ge__(self, other):
        try:
            return self.timetuple() >= other.timetuple()
        except:
            return False


def isoweek(year, week):
    "Iterate over the days in isoweek `week` of `year`."
    # 4th of January is always in week 1
    wk1date = datetime.date(year, 1, 4)

    # daynumber of the 4th, zero-based
    weekday = wk1date.weekday()

    # (proleptic Gregorian) ordinal of first day of week 1
    day1 = wk1date.toordinal() - weekday

    # first day in week
    start = day1 + (week - 1) * 7
    # one past last day in week
    stop = day1 + week * 7

    for n in range(start, stop):
        yield datetime.date.fromordinal(n)


def from_idtag(idtag):
    "Return a class from idtag."
    assert len(idtag) > 1
    assert idtag[0] in 'wdmy'

    return {
        'w': Week,
        'd': Day,
        'm': Month,
        'y': Year,
        }[idtag[0]].from_idtag(idtag)


class Duration(datetime.timedelta):
    "A duration of time."

    @classmethod
    def sum(cls, sequence, start=None):
        """Return the sum of sequence.
           (built-in sum only works with numbers).
        """
        if start is None:
            start = cls(0)
        res = start
        for item in sequence:
            res += item
        return res

    @classmethod
    def parse(cls, txt):
        """Parse a textual representation into a Duration object.
           Format HHH:MM:SS.
        """
        if not txt:
            return None

        time_matcher = re.compile(r"""
            (?:
                (?P<negation>-)
            )?
            (?:
                (?P<weeks>\d+) \W* (?:weeks?|w),?
            )?
            \W*
            (?:
                (?P<days>\d+) \W* (?:days?|d),?
            )?
            \W*
            (?:
                (?P<hours>\d+):
                (?P<minutes>\d+)
                (?::(?P<seconds>\d+)
                (?:\.(?P<microseconds>\d+))?)?
            )?
            """, re.VERBOSE)
        time_matches = time_matcher.match(txt)
        time_groups = time_matches.groupdict()
        keys = time_groups.keys()
        
        if time_groups.get('negation') == '-':
            scale = -1
            keys.remove('negation')
        else:
            scale = 1
        
        for key in keys:
            time_groups[key] = int(time_groups[key]) if time_groups[key] else 0
        time_groups["days"] = time_groups["days"] + (time_groups["weeks"] * 7)
        
        res = cls(
            days=time_groups["days"],
            hours=time_groups["hours"],
            minutes=time_groups["minutes"],
            seconds=time_groups["seconds"])

        return res * scale
    
    def __new__(cls, *args, **kw):
        if len(args) == 1 and isinstance(args[0], datetime.timedelta):
            years = 0
            days = args[0].days
            hours = 0
            minutes = 0
            seconds = args[0].seconds

        else:
            years = kw.get('years', 0)
            days = kw.get('days', 0)
            hours = kw.get('hours', 0)
            minutes = kw.get('minutes', 0)
            seconds = kw.get('seconds', 0)

        # an average year is 365.25 days..
        obj = super(Duration, cls).__new__(cls,
                                           days=days + years * 365,
                                           hours=hours + years * 6,
                                           minutes=minutes,
                                           seconds=seconds)
        return obj

    def __repr__(self):
        dt = self.duration_tuple()
        return '%sDuration(hours=%d, minutes=%d, seconds=%d)' % dt

    def duration_tuple(self):
        "Return self as hours, minutes, seconds."
        seconds = self.toint()
        sign = -1 if seconds < 0 else 1
        seconds *= sign
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return '-' if sign < 0 else '', hours, minutes, seconds

    def __str__(self):
        return '%s%d:%02d:%02d' % self.duration_tuple()

    def __unicode__(self):
        return unicode(str(self))
    
    def toint(self):
        "Convert self to integer."
        return self.seconds + 3600 * 24 * self.days

    __hash__ = datetime.timedelta.__hash__

    def __eq__(self, other):
        if isinstance(other, datetime.timedelta):
            return super(Duration, self).__eq__(other)
        
        if isinstance(other, Duration):
            return self.duration_tuple() == other.duration_tuple()

        if isinstance(other, int) and other == 0:
            return self.toint() == 0

        return False

    def __lt__(self, other):
        if isinstance(other, datetime.timedelta):
            return super(Duration, self).__lt__(other)

        return self.toint() < other.toint()

    def __gt__(self, other):
        if isinstance(other, datetime.timedelta):
            return super(Duration, self).__gt__(other)

        return self.toint() > other.toint()

    def __mul__(self, other):
        return Duration(super(Duration, self).__mul__(other))

    def __add__(self, other):
        return Duration(super(Duration, self).__add__(other))

    def __sub__(self, other):
        return Duration(super(Duration, self).__sub__(other))

    def __div__(self, other):
        if isinstance(other, Duration):
            try:
                return float(self.toint()) / float(other.toint())
            except ZeroDivisionError:
                return 0.0
        return Duration(super(Duration, self).__div__(other))

    def __truediv__(self, other):
        if isinstance(other, Duration):
            try:
                return float(self.toint()) / float(other.toint())
            except ZeroDivisionError:
                return 0.0
        return Duration(super(Duration, self).__truediv__(other))


########################################################################
#  Day


class Day(datetime.date, RangeMixin, CompareMixin):
    "A calendar date."
    
    day_name = u'''mandag tirsdag onsdag torsdag fredag
                   lørdag søndag'''.split()

    day_code = "M U W H F A S".split()

    def __reduce__(self):
        return Day, (self.year, self.month, self.day)

    @classmethod
    def from_idtag(cls, tag):
        "Return Day from idtag."
        if len(tag) == 9:
            # d2008022002
            y, m, d = map(int, fstr(tag).split(1, 5, 7)[1:])
            return cls(y, m, d, membermonth=m)
        else:
            # d2008022002
            y, m, d, b = map(int, fstr(tag).split(1, 5, 7, 9)[1:])
            return cls(y, m, d, membermonth=b)

    @classmethod
    def parse(cls, strval):
        """Parse date value from a string.  Allowed syntax include::

              yyyy-mm-dd, yyyy-m-dd, yyyy-mm-d, yyyy-m-d
              dd-mm-yyyy, etc.
              dd/mm/yyyy, ...
              dd.mm.yyyy, ...
              ddmmyyyy
              
        """
        if not strval or not strval.strip():
            # strval is None or contains only spaces
            return None

        datere = re.compile(r"""
            (?:\s*)
            (?P<isodate>
              (?P<iso_yr>[12]\d{3})
              (?P<sep>[-\./\s])
              (?P<iso_mnth>0[1-9]|1[012]|[1-9])
              (?P=sep)
              (?P<iso_day>3[01]|[12]\d|0[1-9]|[1-9]))
            |(?P<dmy>
              (?P<dmy_day>3[01]|[12]\d|0[1-9]|\d)
              (?P<dmy_sep>[-\.\/\s])
              (?P<dmy_mnth>0[1-9]|1[012]|\d)
              (?P=dmy_sep)
              (?P<dmy_yr>[12]\d{3}))
            |(?P<nsp>
              (?P<nsp_day>3[01]|[12]\d|0[1-9])
              (?P<nsp_mnth>0[1-9]|1[012])
              (?P<nsp_yr>[12]\d{3}))
            |(?P<isonsp>
              (?P<isonsp_yr>20[1-5]\d)
              (?P<isonsp_mnth>0[1-9]|1[012])
              (?P<isonsp_day>3[01]|[12]\d|0[1-9]))
            |(?P<two>
              (?P<two_day>3[01]|[12]\d|0[1-9]|\d)
              (?P<two_sep>[\.\/\s])
              (?P<two_mnth>0[1-9]|1[012]|\d)
              (?P=two_sep)
              (?P<two_yr>[1-9]\d))
            (?:\s*)
        """, re.VERBOSE)
        m = datere.match(strval)
        if not m:
            raise ValueError("Cannot parse %r as date." % strval)

        g = m.groupdict()
        if g['isodate']:
            prefix = 'iso'

        elif g['dmy']:
            prefix = 'dmy'

        elif g['nsp']:
            prefix = 'nsp'

        elif g['isonsp']:
            prefix = 'isonsp'

        elif g['two']:
            prefix = 'two'

        day, month, year = [int(g['%s_%s' % (prefix, val)])
                            for val in ['day', 'mnth', 'yr']]

        if year < 13:
            raise ValueError("Cannot parse %r as date." % strval)
        if year < 100:
            year += 2000

        return cls(year, month, day)
        
    def __new__(cls, *args, **kw):
        if len(args) == 3:
            y, m, d = args
        elif len(args) == 1:
            t = args[0]
            y, m, d = t.year, t.month, t.day
        elif len(args) == 0:
            t = datetime.date.today()
            y, m, d = t.year, t.month, t.day
        else:
            raise TypeError('incorrect number of arguments')

        obj = super(Day, cls).__new__(cls, y, m, d)
        obj.membermonth = kw.get('membermonth', obj.month)
        return obj

    @staticmethod
    def get_day_name(daynum, length=None):
        "Return dayname for daynum."
        if length is None:
            return Day.day_name[daynum]
        else:
            return Day.day_name[daynum][:length]

    def __hash__(self):
        return hash('%04s%02s%02s' % (self.year, self.month, self.day))

    def __repr__(self):
        return '%d-%d-%d-%d' % (self.year, self.month, self.day,
                                self.membermonth)

    def __unicode__(self):
        return u'%04d-%02d-%02d' % (self.year, self.month, self.day)

    def __str__(self):
        if six.PY2:
            return self.__unicode__().encode('u8')
        elif six.PY3:
            return self.__unicode__()

    def datetime(self, hour=0, minute=0, second=0):
        "Extend `self` to datetime."
        return datetime.datetime(self.year, self.month, self.day,
                                 hour, minute, second)

    def date(self):
        "Excplicitly convert to datetime.date."
        return datetime.date(self.year, self.month, self.day)

    def datetuple(self):
        "Return year, month, day."
        return self.year, self.month, self.day

    def __add__(self, n):
        return Day.fromordinal(self.toordinal() + n)

    # make first and last properties, because
    # self.first = self.last = self creates too many cycles :-)
    @property
    def first(self):
        "Define self == self.first for polymorphic usage with other classes."
        return self

    @property
    def last(self):
        "Define self == self.last for polymorphic usage with other classes."
        return self

    def next(self):
        return self + 1

    def prev(self):
        return self - 1

    def __sub__(self, x):
        "Return number of days between Days or Day n days ago."
        if isinstance(x, Day):
            return self.toordinal() - x.toordinal()
        elif isinstance(x, six.integer_types):
            return Day.fromordinal(self.toordinal() - x)
        else:
            raise ValueError('Wrong operands for subtraction: %s and %s'
                             % (type(self), type(x)))

    @property
    def dayname(self):
        "The semi-localized name of self."
        return self.day_name[self.weekday]

    @property
    def code(self):
        "One letter code representing the dayname."
        return self.day_code[self.weekday]

    @property
    def weeknum(self):
        "Return the isoweek of `self`."
        return self.isocalendar()[1]

    @property
    def isoyear(self):
        "Return the `isoyear` of `self`."
        return self.isocalendar()[0]

    @property
    def week(self):
        "Return a Week object representing the week `self` belongs to."
        return Week.weeknum(self.weeknum, self.isoyear)

    @property
    def Month(self):
        "Return a Month object representing the month `self` belongs to."
        return Month(self.year, self.month)

    @property
    def Year(self):
        "Return a Year object representing the year `self` belongs to."
        return Year(self.year)

    @property
    def display(self):
        "Return the 'class' of self."
        res = set()
        if self.today and (self.membermonth == self.month):
            res.add('today')
        if self.in_month:
            res.add('month')
        else:
            res.add('noday')
        if self.weekend:
            res.add('weekend')
        if hasattr(self, 'mark'):
            res.add(self.mark)

        return ' '.join(res)

    @property
    def idtag(self):
        "Return the idtag for `self`: dyyyymmddmm."
        return 'd%d%02d%02d%02d' % (self.year, self.month, self.day,
                                    self.membermonth)

    @property
    def today(self):
        "True if self is today."
        return self.compare(datetime.date.today()) == 'day'

    @property
    def weekday(self):
        "True if self is a weekday."
        return calendar.weekday(self.year, self.month, self.day)

    @property
    def weekend(self):
        "True if self is Saturday or Sunday."
        return 5 <= self.weekday <= 6

    @property
    def special(self):  # pylint:disable=R0201
        "True if the database has an entry for this date (sets special_hours)."
        return False  # for now (XXX)

    @property
    def in_month(self):  # pylint:disable=R0201
        "True iff the day is in its month."
        return self.month == self.membermonth

    def compare(self, other):
        "Return how similar self is to other."
        if self.year == other.year:
            if self.month == other.month:
                if self.day == other.day:
                    return 'day'
                else:
                    return 'month'
            else:
                return 'year'
        else:
            return None

    def _format(self, fmtchars):
        # http://blog.tkbe.org/archive/date-filter-cheat-sheet/
        # pylint:disable=R0912
        #        (too many branches)
        for ch in fmtchars:
            if ch == 'y':
                yield str(self.year)[-2:]
            elif ch == 'Y':
                yield str(self.year)
            elif ch == 'z':
                yield str(self.toordinal() - Day(self.year, 1, 1).toordinal())
            elif ch == 'W':
                yield str(self.weeknum)
            elif ch == 'w':
                yield str(self.weekday)
            elif ch == 'n':
                yield str(self.month)
            elif ch == 'm':
                yield '%02d' % self.month
            elif ch == 'b':
                yield self.Month.format('b')
            elif ch == 'M':
                yield self.Month.format('M')
            elif ch == 'N':
                yield self.Month.format('N')
            elif ch == 'F':
                yield self.Month.format('F')
            elif ch == 'j':
                yield str(self.day)
            elif ch == 'd':
                yield '%02d' % self.day
            elif ch == 'D':
                yield self.dayname[:3]
            elif ch == 'l':
                yield self.dayname
            else:
                yield ch

    def format(self, fmt=None):
        "Emulate Django's date filter."
        if fmt is None:
            fmt = "N j, Y"  # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DATE_FORMAT
        tmp = list(self._format(list(fmt)))
        return ''.join(tmp)


class Today(Day):
    "Special subclass for today's date."
    def __new__(cls, *args, **kw):
        t = datetime.date.today()
        y, m, d = t.year, t.month, t.day
        obj = super(Today, cls).__new__(cls, y, m, d)
        obj.membermonth = obj.month
        return obj

    today = True

########################################################################
#  Days


class Days(list, RangeMixin, CompareMixin):
    "A contigous set of days."
    
    def __init__(self, start, end, start_week=False):
        super(Days, self).__init__()
        assert start <= end
        if start_week:
            start = start - start.weekday  # set to monday
            
        for i in range(start.toordinal(), end.toordinal() + 1):
            self.append(Day.fromordinal(i))

    @property
    def first(self):
        "1st day"
        return self[0]

    @property
    def last(self):
        "last day"
        return self[-1]

########################################################################
#  Week


class Week(RangeMixin, CompareMixin):
    @classmethod
    def from_idtag(cls, tag):
        # w20081
        y = int(tag[1:5])
        w = int(tag[5:])
        return cls.weeknum(w, y)
    
    @classmethod
    def weeknum(cls, n, year=None):
        if year is None:
            year = datetime.date.today().year
        days = list(isoweek(year, n))
        month = days[0].month  # quite arbitrary
        return cls(days, month)        
    
    def __init__(self, days, month):
        super(Week, self).__init__()
        # thursday is always in the correct iso-year per definition
        t = days[3].isocalendar()
        self.year = t[0]
        self.num = t[1]
        self.days = [Day(d, membermonth=month) for d in days]
        self.month = month

    @property
    def current(self):
        "True if today is in week."
        return any(d.today for d in self.days)

    def idtag(self):
        return 'w%d%d' % (self.year, self.num)

    @property
    def first(self):
        "1st day of week."
        return self.days[0]

    @property
    def last(self):
        "Last day of week."
        return self.days[-1]

    def datetuple(self):
        "First day of this week."
        return self.year, self.month, self.first.day

    def __str__(self):
        return 'Uke %d (%d)' % (self.num, self.year)

    def __repr__(self):
        return 'Week(%d, month=%d, year=%d)' % (self.num, self.month, self.year)

    def __iter__(self):
        return iter(self.days)

    def until_today(self):
        for d in self.days:
            if d.today:
                break
            yield d

    def __hash__(self):
        return self.year * 100 + self.num

    def __eq__(self, other):
        return self.year == other.year and self.num == other.num

    def __getitem__(self, n):
        return self.days[n]

    def __contains__(self, date):
        return date in self.days


########################################################################
#  Weeks

class Weeks(list, RangeMixin, CompareMixin):
    def __init__(self, start, end):
        super(Weeks, self).__init__()
        assert start <= end
        for i in range(start, end + 1):
            self.append(Week.weeknum(i))

    @property
    def first(self):
        "First day in first week."
        return self[0][0]

    @property
    def last(self):
        "Last day in last week."
        return self[-1][-1]

    def datetuple(self):
        "First day of first week."
        return self.first.datetuple()

    def dayiter(self):
        "Iterate over all days in all the weeks."
        for wk in self:
            for day in wk:
                yield day

    def __repr__(self):
        return '[' + ', '.join(map(str, iter(self))) + ']'
    
    
########################################################################
#  Month

class Month(RangeMixin, CompareMixin):
    "A calendar month."
    
    month_name = ['', 'Januar', 'Februar', 'Mars', 'April', 'Mai', 'Juni',
                  'Juli', 'August', 'September', 'Oktober', 'November',
                  'Desember']

    @classmethod
    def from_idtag(cls, tag):
        "Parse idtag into `class`:Month."
        # m20082
        y = int(tag[1:5])
        m = int(tag[5:])
        return cls(year=y, month=m)

    @classmethod
    def from_date(cls, d):
        "Create a Month from the date ``d``."
        return cls(year=d.year, month=d.month)

    @classmethod
    def parse(cls, txt):
        """Parse a textual representation into a Month object.
           Format YYYY-MM?
        """
        if not txt:
            return None

        mnth_matcher = re.compile(r"""
            (?P<year>\d{4})-?(?P<month>\d{1,2})
            """, re.VERBOSE)
        m = mnth_matcher.match(txt)
        if not m:
            raise ValueError(
                (u"Ugyldig format, må være åååå-mm, ikke %r." % txt).encode('u8'))
        mnth_groups = m.groupdict()

        return cls(int(mnth_groups["year"]), int(mnth_groups["month"]))

    def __init__(self, year=None, month=None, date=None):
        super(Month, self).__init__()
        if date is not None:
            self.year = date.year
            self.month = date.month
        elif year == month == date == None:
            td = datetime.date.today()
            self.year = td.year
            self.month = td.month
        else:
            assert None not in (year, month)
            self.year = year
            self.month = month

        if not (1 <= self.month <= 12):
            raise ValueError("Month must be in 1..12.")

        self.calendar = calendar.Calendar()
        self.name = self.month_name[self.month]
        self.short_name = self.name[:3]
        #self.short_name = calendar.month_abbr[self.month]
        self.weeks = [Week(days, self.month) for days in self._weeks()]
        #self.day = 1


    def __call__(self, daynum=None):
        """Return the given Day for this year.

           Usage::

               return ttcal.Year().december(23)

        """
        if daynum is None:
            return self  # for when django tries to do value = value() *sigh*
        return Day(self.year, self.month, daynum)

    def __reduce__(self):
        "Deepcopy helper."
        return Month, (self.year, self.month)        

    def __unicode__(self):
        return u"%04d-%02d" % (self.year, self.month)

    @property
    def Year(self):
        "Return a Year object for the year-part of this month."
        return Year(self.year)

    @property
    def Month(self):
        return self

    def __hash__(self):
        return self.year * 100 + self.month

    def __eq__(self, other):
        try:
            return self.year == other.year and self.month == other.month
        except:
            return False

    def __len__(self):
        _, n = calendar.monthrange(self.year, self.month)
        return n

    def datetuple(self):
        "First date in month."
        return self.year, self.month, 1

    def numdays(self):  # for use in template
        "The number of days in the month."
        return len(self)

    def __add__(self, n):
        """Add n months to self."""
        me = self.year * 12 + (self.month - 1)
        me += n
        q, r = divmod(me, 12)
        return Month(q, r + 1)

    def __radd__(self, n):
        return self + n

    def __sub__(self, n):
        if isinstance(n, Month):
            first, last = min(self, n), max(self, n)
            ydiff = last.year - first.year
            mdiff = last.month - first.month
            res = 12 * ydiff + mdiff
            if self > n:
                return res
            return -res
        return self + (-n)

    # rsub doesn't make sense

    def __repr__(self):
        return 'Month(%d, %d)' % (self.year, self.month)

    def __str__(self):
        return '%04d-%02d' % (self.year, self.month)

    def __iter__(self):
        return iter(self.weeks)

    def dayiter(self):
        for wk in self:
            for day in wk:
                yield day

    def days(self):
        "Return a list of days (`class`:ttcal.Day) in this month."
        res = []
        for wk in self:
            for day in wk:
                if day.month == self.month:
                    res.append(day)  # yield day
        return res

    def idtag(self):
        """Return a text representation that is parsable by the from_idtag
           function (above), and is useable as part of an url.
        """
        return 'm%d%d' % (self.year, self.month)

    @property
    def daycount(self):
        "The number of days in this month (as an int)."
        n = calendar.mdays[self.month]
        if self.month == 2 and calendar.isleap(self.year):
            n += 1
        return n

    def prev(self):
        "Previous month."
        return self - 1

    def next(self):
        "Next month."
        return self + 1

    @property
    def first(self):
        "First day in month."
        return Day(self.year, self.month, 1)

    @property
    def last(self):
        "Last day in month."
        return Day(self.year, self.month, self.daycount)

    def _weeks(self):
        c = self.calendar
        return chop(c.itermonthdates(self.year, self.month), 7)

    def __contains__(self, date):
        return self.year == date.year and self.month == date.month

    def __getitem__(self, day):
        for wk in self.weeks:
            for d in wk:
                if d.compare(day) == 'day':
                    return d
        raise KeyError

    def mark(self, d, value='mark', method='replace'):
        try:
            day = self[d]
            if method == 'replace':
                day.mark = value
            elif method == 'append':
                if hasattr(day, 'mark'):
                    day.mark += value
                else:
                    day.mark = value

        except KeyError:
            pass

    def marked_days(self):
        for wk in self.weeks:
            for d in wk:
                if hasattr(d, 'mark'):
                    yield d

    def _format(self, fmtchars):
        # http://blog.tkbe.org/archive/date-filter-cheat-sheet/
        for ch in fmtchars:
            if ch == 'y':
                yield str(self.year)[-2:]
            elif ch == 'Y':
                yield str(self.year)
            elif ch == 'n':
                yield str(self.month)
            elif ch == 'm':
                yield '%02d' % self.month
            elif ch == 'b':
                yield self.name[:3].lower()
            elif ch == 'M':
                yield self.name[:3]
            elif ch == 'N':
                # should be AP style, but doesn't make sense outside US.
                yield self.name[:3]
            elif ch == 'F':
                yield self.name
            else:
                yield ch

    def format(self, fmt=None):
        """Format according to format string. Default format is
           monthname, four-digit-year.
        """
        if fmt is None:
            fmt = "F, Y"
        tmp = list(self._format(list(fmt)))
        return ''.join(tmp)

########################################################################
#  Year


class Year(RangeMixin, CompareMixin):
    def __init__(self, year=None):
        super(Year, self).__init__()
        if year is None:
            year = datetime.date.today().year
        self.year = year
        self.months = [Month(year, i + 1) for i in range(12)]

    def __unicode__(self):
        return unicode(self.year)

    @property
    def Month(self):
        "For orthogonality in the api."
        return self.months[0]

    @property
    def Year(self):
        return self

    @classmethod
    def from_idtag(cls, tag):
        """Year tags have the lower-case letter y + the four digit year,
           eg. y2008.
        """
        y = int(tag[1:5])
        return cls(year=y)

    def idtag(self):
        """Year tags have the lower-case letter y + the four digit year,
           eg. y2008.
        """
        return 'y%d' % self.year

    def marked_days(self):
        for m in self.months:
            for day in m.marked_days():
                yield day

    def datetuple(self):
        "January 1."
        return self.year, 1, 1

    def __add__(self, n):
        """Add n years to self."""
        return Year(self.year + n)

    def __radd__(self, n):
        return self + n

    def __sub__(self, n):
        return self + (-n)

    # rsub doesn't make sense

    def prev(self):
        "Previous year."
        return self - 1

    def next(self):
        "Next year."
        return self + 1

    @property
    def H1(self):
        "First half of this year."
        return self.months[:6]

    @property
    def H2(self):
        "Last half of this year."
        return self.months[6:]

    def halves(self):
        "Both halves of the year."
        return [self.H1, self.H2]

    @property
    def Q1(self):
        "1st quarter."
        return self.months[:3]

    @property
    def Q2(self):
        "2nd quarter."
        return self.months[3:6]

    @property
    def Q3(self):
        "3rd quarter."
        return self.months[6:9]

    @property
    def Q4(self):
        "4th quarter."
        return self.months[9:]

    def quarters(self):
        "Every quarter in this year."
        return [self.Q1, self.Q2, self.Q3, self.Q4]

    #pylint:disable=C0111
    @property
    def january(self):
        return self.months[0]

    @property
    def february(self):
        return self.months[1]

    @property
    def march(self):
        return self.months[2]

    @property
    def april(self):
        return self.months[3]

    @property
    def may(self):
        return self.months[4]

    @property
    def june(self):
        return self.months[5]
    
    @property
    def july(self):
        return self.months[6]

    @property
    def august(self):
        return self.months[7]

    @property
    def september(self):
        return self.months[8]

    @property
    def october(self):
        return self.months[9]

    @property
    def november(self):
        return self.months[10]

    @property
    def december(self):
        return self.months[11]
    #pylint:enable=C0111

    def __repr__(self):
        return 'Year(%d)' % self.year

    def __str__(self):
        return str(self.year)

    def dayiter(self):
        for m in self.months:
            for d in m.days():
                yield d

    def rows(self):
        return chop(iter(self.months), 3)

    def rows4(self):
        return chop(iter(self.months), 4)

    @property
    def first(self):
        "First day of first month."
        return self.months[0].first

    @property
    def last(self):
        "Last day of last month."
        return self.months[-1].last

    def __hash__(self):
        return self.year

    def __eq__(self, other):
        if hasattr(other, 'year'):
            return self.year == other.year
        return False

    def __contains__(self, date):
        return date.year == self.year

    def __getitem__(self, day):
        m = self.months[day.month - 1]
        return m[day]

    def mark_period(self, p, value='mark'):
        d = p.first
        while d != p.last:
            self.mark(d, value)
            d += 1
        self.mark(p.last, value)

    def mark(self, d, value='mark'):
        try:
            self[d].mark = value
        except KeyError:
            pass

    def _format(self, fmtchars):
        # http://blog.tkbe.org/archive/date-filter-cheat-sheet/
        for ch in fmtchars:
            if ch == 'y':
                yield str(self.year)[-2:]
            elif ch == 'Y':
                yield str(self.year)
            else:
                yield ch

    def format(self, fmt=None):
        """Format according to format string. Default format is
           monthname, four-digit-year.
        """
        if fmt is None:
            fmt = "Y"
        tmp = list(self._format(list(fmt)))
        return ''.join(tmp)
