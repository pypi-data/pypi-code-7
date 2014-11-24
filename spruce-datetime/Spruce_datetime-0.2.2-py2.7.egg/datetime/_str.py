"""String formats and representations"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from datetime import datetime as _datetime
from itertools import chain as _chain
import re as _re

import pytz as _tz


ISO8601_DURATION_RE = _re.compile(r'(?P<sign_neg>-)?'
                                   r'(?:(?P<years>\d+)Y)?'
                                   r'(?:(?P<months>\d+)M)?'
                                   r'(?:(?P<days>\d+)D)?'
                                   r'(?:T(?:(?P<hours>\d+)H)?'
                                   r'(?:(?P<minutes>\d+)M)?'
                                   r'(?:(?P<seconds>\d+)'
                                   r'(?P<frac_seconds>\.\d+)?S)?)?$')


RFC5322_MONTH_ABBRS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                       'Sep', 'Oct', 'Nov', 'Dec']
"""
The month name abbreviations specified by the :rfc:`Internet Message
Format Date and Time Specification <5322#section-3.3>`

:type: [:obj:`str`]

"""

RFC5322_MONTH_ABBRS_RE = _re.compile('|'.join(RFC5322_MONTH_ABBRS) + '$')
"""
A regular expression that matches any of the month name abbreviations
specified by the :rfc:`Internet Message Format Date and Time
Specification <5322#section-3.3>`

:type: :class:`re.RegexObject`

"""

RFC5322_OBSOLETE_TZ_HOURS_BY_NAME = {'UT': 0,
                                     'GMT': 0,
                                     'EDT': -4,
                                     'EST': -5,
                                     'CDT': -5,
                                     'CST': -6,
                                     'MDT': -6,
                                     'MST': -7,
                                     'PDT': -7,
                                     'PST': -8,
                                     }
"""
A mapping of names to offset hours for the obsolete time zone names
specified by :rfc:`Internet Message Format Obsolete Date and Time \
<5322#section-4.3>`

:type: {:obj:`str`: :obj:`int`}

"""
for military_tz_name in (chr(ord_) for ord_ in _chain(range(65, 74),
                                                      range(75, 91),
                                                      range(97, 106),
                                                      range(107, 122))):
    RFC5322_OBSOLETE_TZ_HOURS_BY_NAME[military_tz_name] = 0
del military_tz_name

RFC5322_OBSOLETE_TZ_NAMES_RE = \
    _re.compile('|'.join(RFC5322_OBSOLETE_TZ_HOURS_BY_NAME.keys()) + '$')
"""
A regular expression that matches any of the obsolete time zone names
specified by :rfc:`Internet Message Format Obsolete Date and Time \
<5322#section-4.3>`

:type: :class:`re.RegexObject`

"""

RFC5322_OBSOLETE_WEEKDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                  'Friday', 'Saturday', 'Sunday']
"""
The obsolete weekday names specified by :rfc:`Internet Message Format
Obsolete Date and Time <5322#section-4.3>`

"""

RFC5322_OBSOLETE_WEEKDAY_NAMES_RE = \
    _re.compile('|'.join(RFC5322_OBSOLETE_WEEKDAY_NAMES) + '$')
"""
A regular expression that matches any of the obsolete weekday names
specified by :rfc:`Internet Message Format Obsolete Date and Time \
<5322#section-4.3>`

:type: :class:`re.RegexObject`

"""

RFC5322_WEEKDAY_ABBRS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
"""
The weekday abbreviations specified by the :rfc:`Internet Message Format
Date and Time Specification <5322#section-3.3>`

"""

RFC5322_WEEKDAY_ABBRS_RE = _re.compile('|'.join(RFC5322_WEEKDAY_ABBRS) + '$')
"""
A regular expression that matches any of the weekday abbreviations
specified by the :rfc:`Internet Message Format Date and Time
Specification <5322#section-3.3>`

:type: :class:`re.RegexObject`

"""


CTIME_FORMAT_RE = \
    _re.compile(r'(?P<weekday_abbr>{}) (?P<month_abbr>{})'
                 .format(RFC5322_WEEKDAY_ABBRS_RE.pattern[:-1],
                         RFC5322_MONTH_ABBRS_RE.pattern[:-1])
                 + r' (?: ?(?P<day>((?<! )[1-3])?\d))'
                    r' (?P<hour>[0-2]\d):(?P<minute>[0-5]\d)'
                    r':(?P<second>[0-5]\d)'
                    r' (?P<year>\d\d\d\d)$')
"""
A regular expression that matches a date-time string in the format
defined by `asctime()`_

.. _asctime():
    http://pubs.opengroup.org/onlinepubs/009695399/functions/asctime.html

:type: :class:`re.RegexObject`

"""


RFC5322_FORMAT_RE = \
    _re.compile(r'(?:(?P<weekday_abbr>{})|(?P<obsolete_weekday_name>{})),'
                 .format(RFC5322_WEEKDAY_ABBRS_RE.pattern[:-1],
                         RFC5322_OBSOLETE_WEEKDAY_NAMES_RE.pattern[:-1])
                 + r' (?P<day>[0-3]\d) (?P<month_abbr>{}) (?P<year>\d\d\d\d)'
                    .format(RFC5322_MONTH_ABBRS_RE.pattern[:-1])
                 + r' (?P<hour>[0-2]\d):(?P<minute>[0-5]\d)'
                    r':(?P<second>[0-5]\d)'
                    r' (?P<tz>(?:(?P<tz_sign>[-+])(?P<tz_hours>\d\d)'
                    r'(?P<tz_minutes>[0-5]\d))'
                    r'|(?P<obsolete_tz_name>{}))$'
                    .format(RFC5322_OBSOLETE_TZ_NAMES_RE.pattern[:-1]))
"""
A regular expression that matches a date-time string in the format
defined by the :rfc:`Internet Message Format Date and Time
Specification <5322#section-3.3>`

:type: :class:`re.RegexObject`

"""


HTTP11_RFC1123_FORMAT_RE = \
    _re.compile(r'(?P<weekday_abbr>{}), (?P<day>[0-3]\d)'
                 .format(RFC5322_WEEKDAY_ABBRS_RE.pattern[:-1])
                 + r' (?P<month_abbr>{}) (?P<year>\d\d\d\d)'
                    .format(RFC5322_MONTH_ABBRS_RE.pattern[:-1])
                 + r' (?P<hour>[0-2]\d):(?P<minute>[0-5]\d)'
                    r':(?P<second>[0-5]\d)'
                    r' GMT$')
"""
A regular expression that matches a date-time string in the format based
on RFC 1123 that is defined by :rfc:`HTTP/1.1 Full Date \
<2616#section-3.3.1>`

:type: :class:`re.RegexObject`

"""


HTTP11_RFC850_FORMAT_RE = \
    _re.compile(r'(?P<obsolete_weekday_name>{}),'
                 r' (?P<day>[0-3]\d)-(?P<month_abbr>{})-(?P<year_2digit>\d\d)'
                 .format(RFC5322_OBSOLETE_WEEKDAY_NAMES_RE.pattern[:-1],
                         RFC5322_MONTH_ABBRS_RE.pattern[:-1])
                 + r' (?P<hour>[0-2]\d):(?P<minute>[0-5]\d)'
                    r':(?P<second>[0-5]\d)'
                    r' GMT$')
"""
A regular expression that matches a date-time string in the format based
on RFC 850 that is defined by :rfc:`HTTP/1.1 Full Date \
<2616#section-3.3.1>`

:type: :class:`re.RegexObject`

"""


HTTP11_FORMAT_RE = \
    _re.compile('|'.join(r'(?:{})'.format(pattern)
                         for pattern
                         in (HTTP11_RFC1123_FORMAT_RE
                              .pattern[:-1]
                              .replace('(?P<', '(?P<rfc1123_'),
                             HTTP11_RFC850_FORMAT_RE
                              .pattern[:-1]
                              .replace('(?P<', '(?P<rfc850_'),
                             CTIME_FORMAT_RE
                              .pattern[:-1]
                              .replace('(?P<', '(?P<ctime_'),
                             ))
                 + '$')
"""
A regular expression that matches a date-time string in any of the
formats defined by :rfc:`HTTP/1.1 Full Date <2616#section-3.3.1>`

:type: :class:`re.RegexObject`

"""


ISO_LIKE_FORMAT_RE = \
    _re.compile(r'(?P<year>\d{4})'
                 r'(?:[^0-9A-Za-z](?P<month>\d{2})'
                 r'(?:[^0-9A-Za-z](?P<day>\d{2}))?)?'
                 r'(?:(?:T|[^0-9A-Za-z])(?P<hour>\d{2})'
                 r'(?:[^0-9A-Za-z](?P<minute>\d{2})'
                 r'(?:[^0-9A-Za-z](?P<second>\d{2})'
                 r'(?:[^0-9A-Za-z](?P<microsecond>\d{1,6}))?)?)?)?'
                 r'(?:[^0-9A-Za-z]?'
                 r'(?P<tz_sign>(?:(?<=[^0-9A-Za-z])[+-]?)|[+-])'
                 r'(?P<tz_hours>\d{1,2})'
                 r'(?:[^0-9A-Za-z]?(?P<tz_minutes>\d{2}))?)?$')
"""
A regular expression that matches a date-time string in a format that
looks roughly like ISO 8601 dates and date-times

:type: :class:`re.RegexObject`

"""


def datetime_httpstr(dt):
    """The HTTP date-time string representation of a date-time

    .. seealso:: :rfc:`HTTP/1.1 Full Date <2616#section-3.3.1>`

    :param dt:
        A date-time.
    :type dt: :class:`datetime.datetime`

    :rtype: :obj:`str`

    """
    return dt.astimezone(_tz.UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')


def datetime_from_re_match(string,
                           re,
                           re_flags=0,
                           year_group='year',
                           month_group='month',
                           day_group='day',
                           hour_group='hour',
                           minute_group='minute',
                           second_group='second',
                           microsecond_group='microsecond',
                           tz_sign_group='tz_sign',
                           tz_hours_group='tz_hours',
                           tz_minutes_group='tz_minutes',
                           default_tz=None):

    """
    Parse a date-time from a date-time string according to a regular
    expression

    The given *string* is parsed with the given regular expression *re*,
    extracted to date-time parts using the corresponding named match groups,
    and converted to a :class:`~datetime.datetime`.  These rules apply:

      * The date-time parts are extracted as named :obj:`match groups
        <re.MatchObject.group>`, using the names specified by the
        corresponding *\*_group* arguments.

      * A match is required, but none of the expected parts is required to
        be matched.  If desired, such requirements can be expressed in the
        *re* by making it match only if all desired parts are present.

      * If the year part is omitted, it defaults to :code:`'1970'`.

      * If either of the month or day parts is omitted, it defaults to
        :code:`'1'`.

      * If any time part (hour, minute, second, microsecond) is omitted, it
        defaults to :code:`'0'`.

      * If a time zone is specified:

        * It must contain at least a sign part and an hours part.

        * The sign part must be a positive sign (:code:`'+'` or :code:`''`)
          or a negative sign (:code:`'-'`).

        * The minutes part, if omitted, defaults to :code:`'0'`.

        * The resulting :class:`~datetime.datetime` is time-zone-aware.

        * The resulting time zone is a fixed offset of minutes equal to
          the result of evaluating the arithmetic expression
          :samp:`{tz_sign}({tz_hours} * 60 + {tz_minutes})` after
          substituting the corresponding time zone parts.

      * If a time zone is omitted, it defaults to *default_tz*.  If this is
        null, then the resulting :class:`~datetime.datetime` is
        time-zone-naive.

    :param str string:
        A date-time string.

    :param re:
        A regular expression.
    :type re: ~\ :func:`re.compile`

    :param int re_flags:
        Regular expression flags passed to :func:`re.compile`.

    :param str year_group:
        The name of the *re* match group that captures the year.

    :param str month_group:
        The name of the *re* match group that captures the month.

    :param str day_group:
        The name of the *re* match group that captures the day.

    :param str hour_group:
        The name of the *re* match group that captures the hour.

    :param str minute_group:
        The name of the *re* match group that captures the minute.

    :param str second_group:
        The name of the *re* match group that captures the second.

    :param str microsecond_group:
        The name of the *re* match group that captures the microsecond.

    :param str tz_sign:
        The name of the *re* match group that captures the time zone offset
        sign.

    :param str tz_hours:
        The name of the *re* match group that captures the time zone offset
        hours.

    :param str tz_minutes:
        The name of the *re* match group that captures the time zone offset
        minutes.

    :param default_tz:
        The default time zone.
    :type default_tz: :class:`datetime.tzinfo` or null

    :rtype: :class:`datetime.datetime`

    """

    re = _re.compile(re, re_flags)

    match = re.match(string)
    if match:
        dt_args = []

        for name, default in ((year_group, 1970),
                              (month_group, 1),
                              (day_group, 1),
                              (hour_group, 0),
                              (minute_group, 0),
                              (second_group, 0),
                              (microsecond_group, 0),
                              ):
            value_str = match.group(name)
            if value_str is not None:
                try:
                    value = int(value_str)
                except (TypeError, ValueError):
                    raise ValueError('invalid date-time regex {!r}: group {!r}'
                                      ' matched non-integer string {!r}'
                                      .format(re.pattern, name, value_str))
            else:
                value = default
            dt_args.append(value)

        tz_sign_str = match.group(tz_sign_group)
        if tz_sign_str is not None:
            if tz_sign_str in ('+', ''):
                tz_sign = 1
            elif tz_sign_str == '-':
                tz_sign = -1
            else:
                raise ValueError('invalid date-time regex {!r}: group {!r}'
                                  ' matched non-sign string {!r}'
                                  .format(re.pattern, tz_sign_group,
                                          tz_sign_str))

            tz_hours_str = match.group(tz_hours_group)
            try:
                tz_hours = int(tz_hours_str)
            except (TypeError, ValueError):
                raise ValueError('invalid date-time regex {!r}: group {!r}'
                                  ' matched non-integer string {!r}'
                                  .format(re.pattern, tz_hours_group,
                                          tz_hours_str))

            tz_minutes_str = match.group(tz_minutes_group)
            if tz_minutes_str is not None:
                try:
                    tz_minutes = int(tz_minutes_str)
                except (TypeError, ValueError):
                    raise ValueError('invalid date-time regex {!r}: group {!r}'
                                      ' matched non-integer string {!r}'
                                      .format(re.pattern, tz_minutes_group,
                                              tz_minutes_str))
            else:
                tz_minutes = 0

            tz_minutes += tz_hours * 60
            tz_minutes *= tz_sign
            tz = _tz.FixedOffset(tz_minutes)

        else:
            tz = default_tz
        dt_args.append(tz)

        return _datetime(*dt_args)

    else:
        raise ValueError('invalid date-time string {!r}; expecting a string'
                          ' that matches regex {!r}'
                          .format(string, re.pattern))


def datetime_from_httpstr(string):

    """Convert an HTTP date-time string to a date-time object

    .. seealso:: :rfc:`HTTP/1.1 Full Date <2616#section-3.3.1>`

    :param str string:
        An HTTP date-time string.

    :rtype: :class:`datetime.datetime`

    """

    match = HTTP11_FORMAT_RE.match(string)

    if not match:
        raise ValueError('invalid HTTP date-time string {!r}; expecting a'
                          ' string in one of the formats specified in RFC 2616'
                          ' section 3.3.1'
                          .format(string))

    year_str = match.group('rfc1123_year')
    if year_str:
        year = int(year_str)
    else:
        year_str = match.group('rfc850_year_2digit')
        if year_str:
            # CAVEAT: guess the year meant by a two-digit year, as specified by
            #   :rfc:`HTTP/1.1 Tolerant Applications <2616#section-19.3>`
            year = 2000 + int(year_str)
            if year > _datetime.now().year + 50:
                year -= 100
        else:
            year = int(match.group('ctime_year'))

    month_abbr = _http11_format_re_match_pseudogroup(match, 'month_abbr')
    month = 1 + RFC5322_MONTH_ABBRS.index(month_abbr)

    day = int(_http11_format_re_match_pseudogroup(match, 'day'))
    hour = int(_http11_format_re_match_pseudogroup(match, 'hour'))
    minute = int(_http11_format_re_match_pseudogroup(match, 'minute'))
    second = int(_http11_format_re_match_pseudogroup(match, 'second'))

    return _datetime(year, month, day, hour, minute, second, tzinfo=_tz.UTC)


def _http11_format_re_match_pseudogroup(match, name):
    return match.group('rfc1123_{}'.format(name)) \
           or match.group('rfc850_{}'.format(name)) \
           or match.group('ctime_{}'.format(name))
