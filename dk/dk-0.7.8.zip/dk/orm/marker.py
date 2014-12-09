# -*- coding: utf-8 -*-

"""Finding correct placeholder token..
"""

import datetime


def marker(val):
    "Introspect type of ``val`` and return correct placeholder for db."
    if isinstance(val, basestring):
        return '%s'
    if isinstance(val, (int, long, bool)):
        return '%d'
    if isinstance(val, float):
        return '%f'
    if isinstance(val, (datetime.date, datetime.datetime)):
        return '%s'
    if val is None:
        return '%s'

    raise ValueError("I don't know the marker for type %s (%s)" % (type(val),
                                                                   repr(val)))


def marker_type(t):
    "Different data-types have different placeholders..."
    if t in (str, unicode):
        return '%s'
    if t in (int, long, bool):
        return '%d'
    if t == float:
        return '%f'
    if t in (datetime.date, datetime.datetime):
        return '%s'

    raise ValueError("I don't know the marker for type %s." % repr(t))
