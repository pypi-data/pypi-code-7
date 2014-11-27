# -*- coding: utf-8 -*-
"""For the moment, this is pretty much all of direg. __init__.py imports all of this module.
"""

import logging
logger = logging.getLogger(__name__)

import os
import imp
import sys
import inspect

registries = []


def load_module(name, path):
    """Load and return module object at "path"
    """
    try:
        module = imp.load_source(name, path)
    except IOError:
        logger.info('{0}: no such file'.format(path))
        module = imp.new_module(name)
        module.data = {}
    return module


def get_registry_data(registries):
    """Merge and return the namespaces of modules listed in iterable "registries"
    """
    data = {}
    for registry in registries:
        module = load_module('_module', registry)
        data.update(module.data)
    return data


def get_class_from_frame(fr):
    args, _, _, value_dict = inspect.getargvalues(fr)
    if len(args) and args[0] == 'self':
        instance = value_dict.get('self', None)
        if instance:
            return getattr(instance, '__class__', None).__name__
    return None


def compute_key(s):
    frame = sys._getframe().f_back
    frame = frame.f_back
    fun_name = frame.f_code.co_name
    if fun_name == '<module>':
        fun_name = ''
    components = []
    mod_name = inspect.getmodule(frame.f_code).__name__
    components.append(mod_name)
    zclass = get_class_from_frame(frame)
    if zclass is not None:
        components.append(zclass)
    if fun_name:
        components.append(fun_name)
    components.append(s)
    key = '.'.join(components)
    return key


def get_value(s):
    """Look up key in a given context. For example, in a module called "foo", if we have:

            class Bar:
                def meth(self):
                    return get_value('my_var')

            b = Bar()
            x = b.meth()

        Then the registry/registries will be consulted for a key 'foo.Bar.meth.my_var' and it's corresponding value
        will be returned.
    """
    key = compute_key(s)
    value = get_registry_data(registries)[key]
    return value
