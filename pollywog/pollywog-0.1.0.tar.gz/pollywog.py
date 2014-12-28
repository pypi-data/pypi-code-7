"""
Syntactic sugar for working with regular expressions in Python.
"""

__author__ = 'Charles Leifer'
__license__ = 'MIT'
__version__ = '0.1.0'

import re


class _R(type):
    def __div__(self, regex):
        return R(regex)
    __truediv__ = __div__


class R(_R('R', (object,), {})):
    def __init__(self, regex, *args, **kwargs):
        self._regex = re.compile(regex, *args, **kwargs)

    def __div__(self, s):
        return RegexOperation(self._regex, s)
    __truediv__ = __div__


class RegexOperation(object):
    def __init__(self, regex, search):
        self._regex = regex
        self._search = search

    def search(self, as_dict=False):
        match = self._regex.search(self._search)
        if match is None:
            return

        if as_dict:
            return match.groupdict()
        else:
            return match.groups()

    def __len__(self):
        return self.search() is not None

    def __div__(self, replacement):
        return self._regex.sub(replacement, self._search)
    __truediv__ = __div__

    def __iter__(self):
        return self.iter_tuples()

    def iter_matches(self, start_idx=None, end_idx=None):
        # The re module is finicky about arguments, since the indexes cannot be None
        # to indicate *default value*.
        if start_idx and end_idx:
            args = (self._search, start_idx, end_idx)
        elif start_idx:
            args = (self._search, start_idx)
        elif end_idx:
            args = (self._search, 0, end_idx)
        else:
            args = (self._search,)
        for result in self._regex.finditer(*args):
            yield result

    def iter_tuples(self, start_idx=None, end_idx=None):
        for result in self.iter_matches(start_idx, end_idx):
            yield result.groups()

    def iter_dicts(self, start_idx=None, end_idx=None):
        for result in self.iter_matches(start_idx, end_idx):
            yield result.groupdict()
