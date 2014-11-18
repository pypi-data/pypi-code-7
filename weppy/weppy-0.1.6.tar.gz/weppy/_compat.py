# -*- coding: utf-8 -*-
"""
    weppy._compat
    -------------

    Some py2/py3 compatibility support.

    :copyright: (c) 2014 by Giovanni Barillari
    :license: BSD, see LICENSE for more details.
"""

import sys

PY2 = sys.version_info[0] == 2
_identity = lambda x: x

if PY2:
    from Cookie import SimpleCookie
    from cStringIO import StringIO
    import cPickle as pickle
    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()
    integer_types = (int, long)

    def reraise(tp, value, tb=None):
        raise tp, value, tb
else:
    from http.cookies import SimpleCookie
    from io import StringIO
    import pickle
    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())
    integer_types = (int, )

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
