
import sys, copy
from itertools import groupby, count, chain
import re

_PY3 = sys.version_info[0] > 2
if _PY3:
    basestring = str

SPANRE = re.compile(r'^\s*(?P<start>-?\d+)\s*(-\s*(?P<stop>-?\d+))?\s*$')
class ParseError(ValueError):
    pass

class intspan(set):
    def __init__(self, initial=None):
        super(intspan, self).__init__()
        if initial:
            self.update(initial)

    def copy(self):
        return copy.copy(self)

    def update(self, items):
        super(intspan, self).update(self._parse_range(items))
        return self

    def intersection_update(self, items):
        super(intspan, self).intersection_update(self._parse_range(items))
        return self

    def difference_update(self, items):
        super(intspan, self).difference_update(self._parse_range(items))
        return self

    def symmetric_difference_update(self, items):
        super(intspan, self).symmetric_difference_update(self._parse_range(items))
        return self

    def discard(self, items):
        for item in self._parse_range(items):
            super(intspan, self).discard(item)

    def remove(self, items):
        for item in self._parse_range(items):
            super(intspan, self).remove(item)

    def add(self, items):
        for item in self._parse_range(items):
            super(intspan, self).add(item)

    def issubset(self, items):
        return super(intspan, self).issubset(self._parse_range(items))

    def issuperset(self, items):
        return super(intspan, self).issuperset(self._parse_range(items))

    def union(self, items):
        return intspan(super(intspan, self).union(self._parse_range(items)))

    def intersection(self, items):
        return intspan(super(intspan, self).intersection(self._parse_range(items)))

    def difference(self, items):
        return intspan(super(intspan, self).difference(self._parse_range(items)))

    def symmetric_difference(self, items):
        return intspan(super(intspan, self).symmetric_difference(self._parse_range(items)))

    __le__   = issubset
    __ge__   = issuperset
    __or__   = union
    __and__  = intersection
    __sub__  = difference
    __xor__  = symmetric_difference
    __ior__  = update
    __iand__ = intersection_update
    __isub__ = difference_update
    __ixor__ = symmetric_difference_update

    def __eq__(self, items):
        return super(intspan, self).__eq__(self._parse_range(items))

    def __lt__(self, items):
        return super(intspan, self).__lt__(self._parse_range(items))

    def __gt__(self, items):
        return super(intspan, self).__gt__(self._parse_range(items))

    def __iter__(self):
        """
        Iterate in ascending order.
        """
        return iter(sorted(super(intspan, self).__iter__()))

    def pop(self):
        min_item = min(self)
        self.discard(min_item)
        return min_item

        # this method required only for PyPy, which otherwise gets the wrong
        # answer (unordered)

    @classmethod
    def from_ranges(cls, ranges):
        return cls( chain( *(range(r[0], r[1]+1) for r in ranges) ) )

    @staticmethod
    def _parse_range(datum):

        def parse_chunk(chunk):
            """
            Parse each comma-separated chunk. Hyphens (-) can indicate ranges,
            or negative numbers. Returns a list of specified values. NB Designed
            to parse correct input correctly. Results of incorrect input are
            undefined.
            """
            m = SPANRE.search(chunk)
            if m:
                start = int(m.group('start'))
                if m.group('stop'):
                    stop = int(m.group('stop'))
                    return list(range(start, stop+1))
                return [ start ]
            else:
                raise ParseError("Can't parse chunk '{0}'".format(chunk))

        if isinstance(datum, basestring):
            result = []
            for part in datum.split(','):
                result.extend(parse_chunk(part))
            return result
        else:
            return datum if hasattr(datum, '__iter__') else [ datum ]

    @staticmethod
    def _as_range(iterable):
        l = list(iterable)
        if len(l) > 1:
            return (l[0], l[-1])
        else:
            return (l[0], l[0])

    @staticmethod
    def _as_range_str(iterable):
        l = list(iterable)
        if len(l) > 1:
            return '{0}-{1}'.format(l[0], l[-1])
        else:
            return '{0}'.format(l[0])

    def __repr__(self):
        """
        Return the representation.
        """
        return 'intspan({0!r})'.format(self.__str__())

    def __str__(self):
        """
        Return the stringification.
        """
        items = sorted(self)
        return ','.join(self._as_range_str(g) for _, g in groupby(items, key=lambda n, c=count(): n-next(c)))

    def ranges(self):
        """
        Return a list of the set's contiguous (inclusive) ranges.
        """
        items = sorted(self)
        return [ self._as_range(g) for _, g in groupby(items, key=lambda n, c=count(): n-next(c)) ]

    # see Jeff Mercado's answer to http://codereview.stackexchange.com/questions/5196/grouping-consecutive-numbers-into-ranges-in-python-3-2
    # see also: http://stackoverflow.com/questions/2927213/python-finding-n-consecutive-numbers-in-a-list


# It might be interesting to have a metaclass factory that could create
# spansets of things other than integers. For example, enumerateds defined
# by giving a universe of possible options. Or characters.