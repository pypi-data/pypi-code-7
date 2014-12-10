# -*- coding: utf-8 -*-

"""Utility functions.
"""
from collections import OrderedDict
from .bsd_checksum import bsd_checksum  # make name available from this module


def n_(s, replacement='_'):
    """Make binary fields more readable.
    """
    if isinstance(s, (str, unicode, bytearray)):
        return s.replace('\0', replacement)
    return s


def split_string(s, *ndxs):
    """String sub-class with a split() method that splits a given indexes.

       Usage:

          >>> print split_string('D2008022002', 1, 5, 7, 9)
          ['D', '2008', '02', '20', '02']

    """
    if len(ndxs) == 0:
        return [s]
    if len(ndxs) == 1:
        i = ndxs[0]
        return [s[:i], s[i:]]

    res = []
    b = 0
    while ndxs:
        a, b, ndxs = b, ndxs[0], ndxs[1:]
        res.append(s[a:b])
    res.append(s[b:])

    return res


def split_fields(s, sizes):
    """Split a string into fields based on field `sizes`.
    """
    slen = len(s)
    if None in sizes:
        nonesize = slen - sum(v for v in sizes if v is not None)
        sizes = [v or nonesize for v in sizes]
    ndxs = [sizes[0]]
    cur = 1
    while cur < len(sizes) - 1:
        ndxs.append(ndxs[-1] + sizes[cur])
        cur += 1
    return split_string(s, *ndxs)


class pset(OrderedDict):
    """A property set is an OrderedDict with prettier string display
       (useful when working with record lengths that are wider than your
       terminal).
    """
    def __repr__(self):
        return '{%s}' % ', '.join('%s: %r' % (str(k), str(v))
                                  for k,v in self.items())

    def __str__(self):
        return "{\n%s\n}" % ',\n'.join('    %s: %r' % (str(k), str(v))
                                       for k,v in self.items())


def pad(data, size, padchar=' '):
    """Pad the `data` to exactly length = `size`.
    """
    if len(data) > size:
        raise ValueError("Data is longer than size, cannot pad.")
    if len(data) == size:
        return data
    return data + padchar * (size - len(data))


