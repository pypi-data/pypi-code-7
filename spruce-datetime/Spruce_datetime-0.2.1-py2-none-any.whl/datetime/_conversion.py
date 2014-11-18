"""Conversions"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from calendar import timegm as _unixtime_from_utc_timestruct
from datetime import datetime as _datetime
import os as _os
from time import mktime as _unixtime_from_localtime_timestruct

import pytz as _pytz

from . import _tz


def datetime_from_localtime_timestruct(timestruct):
    """Convert a local-time time struct to a UTC date-time object

    The input is assumed to be in local time.  The resulting
    :class:`~datetime.datetime` is in UTC and is time-zone-aware.

    :param timestruct:
        A time struct.
    :type timestruct: :class:`time.struct_time`

    :rtype: :class:`datetime.datetime`

    """
    return datetime_from_unixtime(_unixtime_from_localtime_timestruct
                                   (timestruct))


def datetime_from_unixtime(unixtime):
    """Convert a Unix time to a UTC date-time object

    Unix time is defined in UTC.  The resulting :class:`~datetime.datetime`
    is in UTC and is time-zone-aware.

    :param int unixtime:
        A time struct.

    :rtype: :class:`datetime.datetime`

    """
    return _datetime.fromtimestamp(unixtime, _pytz.UTC)


def datetime_from_utc_timestruct(timestruct):
    """Convert a UTC time struct to a UTC date-time object

    The input is assumed to be in UTC.  The resulting
    :class:`~datetime.datetime` is in UTC and is time-zone-aware.

    :param timestruct:
        A time struct.
    :type timestruct: :class:`time.struct_time`

    :rtype: :class:`datetime.datetime`

    """
    return naive_datetime_from_timestruct(timestruct).replace(tzinfo=_pytz.UTC)


def datetime_with_named_tz(dt, tzname):

    """Assign a named time zone to a date-time

    .. warning::
        This function will go away after the relevant bug is fixed in
        :mod:`pytz`.

    This works around a bug in :mod:`pytz` (from :pypi:`pytz`) when it comes
    to handling time zones that consist of DST and non-DST counterparts.

    If the :mod:`pytz` bug was fixed, then this would be equivalent to

    .. parsed-literal::

        *dt*.replace(tzinfo=pytz.timezone(*tzname*))

    .. warning::
        This function has been tested only on GNU/Linux.

    :param dt:
        A date-time.
    :type dt: :class:`datetime.datetime`

    :param str tzname:
        The name of a time zone.  One of the relative file paths under
        :file:`/usr/share/zoneinfo/`.

    :rtype: :class:`datetime.datetime`

    """

    _os.environ['TZ'] = tzname
    _tz.tzset()

    tz = _pytz.FixedOffset(_tz.LOCALTIME.utcoffset(dt).total_seconds()
                            / 60)
    dt_withtz = dt.replace(tzinfo=tz)

    del _os.environ['TZ']
    _tz.tzset()

    return dt_withtz


def localtime_datetime_from_localtime_timestruct(timestruct):
    """Convert a local-time time struct to a local-time date-time object

    The input is assumed to be in local time.  The resulting
    :class:`~datetime.datetime` is in local time and is time-zone-aware.

    :param timestruct:
        A time struct.
    :type timestruct: :class:`time.struct_time`

    :rtype: :class:`datetime.datetime`

    """
    return naive_datetime_from_timestruct(timestruct)\
            .replace(tzinfo=_tz.LOCALTIME)


def localtime_datetime_from_unixtime(unixtime):
    """Convert a Unix time to a local-time date-time object

    Unix time is defined in UTC.  The resulting :class:`~datetime.datetime`
    is in local time and is time-zone-aware.

    :param int unixtime:
        A Unix time.

    :rtype: :class:`datetime.datetime`

    """
    return _datetime.fromtimestamp(unixtime, _tz.LOCALTIME)


def naive_datetime_from_timestruct(timestruct):
    """Convert a time struct to a time-zone-naive date-time object

    The input and the result express the same time in the same time zone,
    but that time zone is not specified.  Consequently, the resulting
    :class:`~datetime.datetime` is time-zone-naive.

    :param timestruct:
        A time struct.
    :type timestruct: :class:`time.struct_time`

    :rtype: :class:`datetime.datetime`

    """
    return _datetime(timestruct.tm_year, timestruct.tm_mon, timestruct.tm_mday,
                     timestruct.tm_hour, timestruct.tm_min, timestruct.tm_sec)


def unixtime_from_datetime(dt):
    """Convert a :class:`datetime.datetime` to a Unix time

    If the given *datetime* is time-zone-aware, then it is converted to UTC
    before being converted to Unix time.  Otherwise it is converted directly
    to Unix time, regardless of the value of :samp:`{datetime}.dst()`; in
    this case, it is up to the caller to ensure that *datetime* is in UTC.

    :param dt:
        A date-time.
    :type dt: :class:`datetime.datetime`

    :rtype: :obj:`int`

    """
    return _unixtime_from_utc_timestruct(dt.utctimetuple())
