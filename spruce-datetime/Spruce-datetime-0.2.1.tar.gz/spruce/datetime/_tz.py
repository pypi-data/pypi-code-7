"""Time zones

See :mod:`pytz` from :pypi:`pytz` for :class:`~datetime.tzinfo` objects
for other time zones.

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from datetime import timedelta as _timedelta, tzinfo as _tzinfo
import time as _localtime
from time \
    import mktime as _unixtime_from_localtime_timestruct, \
           localtime as _localtime_timestruct_from_unixtime, \
           tzset as _tzset


_TIMEDELTA_ZERO = _timedelta(0)

_TIMEDELTA_DST = _TIMEDELTA_ZERO

_TIMEDELTA_DSTSTD = _TIMEDELTA_ZERO

_TIMEDELTA_STD = _TIMEDELTA_ZERO


def tzset():

    """
    Reset the local time conversion rules per environment variable
    :envvar:`TZ`

    .. seealso:: :func:`time.tzset`

    """

    _tzset()

    global _TIMEDELTA_DST, _TIMEDELTA_DSTSTD, _TIMEDELTA_STD
    _TIMEDELTA_STD = _timedelta(seconds=-_localtime.timezone)
    if _localtime.daylight:
        _TIMEDELTA_DST = _timedelta(seconds=-_localtime.altzone)
    else:
        _TIMEDELTA_DST = _TIMEDELTA_STD
    _TIMEDELTA_DSTSTD = _TIMEDELTA_DST - _TIMEDELTA_STD

tzset()


class _LocalTime(_tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return _TIMEDELTA_DST
        else:
            return _TIMEDELTA_STD

    def dst(self, dt):
        if self._isdst(dt):
            return _TIMEDELTA_DSTSTD
        else:
            return _TIMEDELTA_ZERO

    def tzname(self, dt):
        return _localtime.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        timestruct = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
                      dt.weekday(), 0, 0)
        unixtime = _unixtime_from_localtime_timestruct(timestruct)
        timestruct = _localtime_timestruct_from_unixtime(unixtime)
        return timestruct.tm_isdst > 0

LOCALTIME = _LocalTime()
"""The local time zone

Adapted from the example `tzinfo objects
<http://docs.python.org/library/datetime.html#tzinfo-objects>`_.

:type: :class:`datetime.tzinfo`

"""
