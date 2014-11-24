"""Miscellany"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from datetime import datetime as _datetime

import pytz as _pytz

from . import _tz


def now():
    """The current UTC date-time

    The resulting :class:`~datetime.datetime` is time-zone-aware, unlike
    the result of :meth:`datetime.utcnow() <datetime.datetime.utcnow>`.

    :rtype: :class:`datetime.datetime`

    """
    return _datetime.now(_pytz.UTC)


def now_localtime():
    """The current local-time date-time

    The resulting :class:`~datetime.datetime` is time-zone-aware, unlike
    the result of calling :meth:`datetime.now() <datetime.datetime.now>`
    with no argument.

    :rtype: :class:`datetime.datetime`

    """
    return _datetime.now(_tz.LOCALTIME)
