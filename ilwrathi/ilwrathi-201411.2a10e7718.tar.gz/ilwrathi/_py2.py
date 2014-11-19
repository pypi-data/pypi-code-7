#!/usr/bin/env python2
from types import FunctionType as _fntype

class _IACMeta(type):
    
    def __new__(meta, name, bases, dct):
        keys = [k[4:] for k,v in dct.items()
                if k.startswith('get_') and type(v) == _fntype]
        dct["_keys"] = keys
        return super(_IACMeta, meta).__new__(meta,
                                             name,
                                             bases,
                                             dct)
    def __init__(cls, name, bases, dct):
        old_init = cls.__init__
        def init(self, *args, **kwargs):
            self._cur_values = {}
            self.history = []
            self.name = kwargs.get("name") or "undefined"
            old_init(self, *args, **kwargs)
        cls.__init__ = init
        super(_IACMeta, cls).__init__(name, bases, dct)


class IACBase(object):
    __metaclass__ = _IACMeta

    def iterkeys(self):
        """D.iterkeys() -> an iterator over the keys of D"""
        #This should be done with a metaclass
        return (k for k in self._keys)

    def itervalues(self):
        """D.values() -> list of D's values"""
        return (self[k] for k in self.iterkeys())
        
    def values(self):
        """D.values() -> list of D's values"""
        return [v for v in self.itervalues()]

    def iteritems(self):
        """D.iteritems() -> an iterator over the (key, value) items of D"""
        return ((k,v) for k,v in zip(self.iterkeys(), self.itervalues()))

    def items(self):
        """D.items() -> list of D's (key, value) pairs, as 2-tuples"""
        return [(k,v) for k,v in self.iteritems()]

    
