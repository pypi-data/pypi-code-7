#!/usr/bin/env python3
from types import FunctionType as _fntype
from inspect import signature

class _IACMeta(type):

    def __new__(meta, name, bases, dct):
        #may be able to share this with py2
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
        init.__signature__ = signature(old_init)
        cls.__init__ = init
        super(_IACMeta, cls).__init__(name, bases, dct)


class IACBase(object, metaclass=_IACMeta):

    def values(self):
        """D.values() -> list of D's values"""
        return [self[k] for k in self.keys()]

    def items(self):
        """D.iteritems() -> an iterator over the (key, value) items of D"""
        #is this the behavior I want?
        return dict((k,v) for k,v in zip(self.keys(), self.values())).items()



