# coding: utf-8
from __future__ import print_function

import functools


def rpc_method(func, name=None):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        attr_name = '__rpc_method_name_%s' % func.__name__
        attr_value = name
        if name is None:
            attr_value = func.__name__
        setattr(func.__objclass__, attr_name, attr_value)
        return func(*args, **kwargs)

    return wrapped


