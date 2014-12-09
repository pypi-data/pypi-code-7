""" goulash.wrappers
"""

class JSONWrapper(object):
    # convenience wrapper that makes __getattr__
    # work via __getitem__
    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            return getattr(self._data, name)
    __getitem__ = __getattr__

class DumbWrapper(object):
    # Simplest wrapper pattern
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, x):
        return getattr(self.obj, x)

    def __iter__(self):
        return iter(self.obj)
