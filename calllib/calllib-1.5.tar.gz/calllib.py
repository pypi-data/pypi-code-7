########################################################################
# A library for calling callables with runtime-defined parameters.
#
# Copyright 2005-2014 True Blade Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Notes:
#  Uses the inspect module to compute actual function arguments.
########################################################################

import inspect as _inspect
import types as _types
import sys as _sys

__all__ = ['apply', 'getargs', 'inspect_params']

_PY2 = _sys.version_info[0] == 2
_PY3 = _sys.version_info[0] == 3

try:
    from itertools import izip as _zip
except ImportError:
    # this needs to be named _zip so as to not export zip when
    #  running in Python 2.x
    _zip = zip

def _get_arg(args_dict, arg_name, arg_num, n_args, defaults):
    try:
        # look this up in the dictionary of arguments, if it's present
        return args_dict[arg_name]
    except KeyError:
        pass

    # not in the dictionary, see if a default exists for this argument
    try:
        return defaults[arg_num - n_args]
    except (IndexError, TypeError):
        # TypeError if defaults is None
        # IndexError if no default for this argument
        raise ValueError('no value and no default for %r' % arg_name)


def _get_callable_info(fn):
    # return a list of argument_names, and a list of default values

    if _PY2:
        # see if this is really an object with a __call__ method
        if type(fn) == _types.InstanceType:
            try:
                fn = fn.__call__
            except AttributeError:
                raise TypeError('calllib unsupported type %r' % fn)

        # if this is a new or old style class, look at the __init__ method
        if type(fn) == _types.ClassType:
            # old style class
            nskip = 1
            try:
                fn = fn.__init__
            except AttributeError:
                # no __init__, so this can be called with
                #  no params
                return [], []

        elif type(fn) == _types.TypeType:
            # new style class
            # there's always an __init__ function, for object if not for the
            #  class itself
            nskip = 1
            fn = fn.__init__

            # can't inspect object.__init__, so just say it has
            #  no params and no defaults
            if fn is object.__init__:
                return [], []

        elif type(fn) == _types.FunctionType:
            nskip = 0

        elif type(fn) == _types.MethodType:
            # bound method?
            if fn.im_self is None:
                nskip = 0
            else:
                nskip = 1
        else:
            raise TypeError('calllib unsupported type %r' % fn)
    else:
        if hasattr(fn, '__call__') and _inspect.ismethod(fn.__call__):
            fn = fn.__call__

        # if this is a class, look at the __init__ method
        if _inspect.isclass(fn):
            # new style class
            # there's always an __init__ function
            nskip = 1
            fn = fn.__init__

            # can't inspect object.__init__, so just say it has
            #  no params and no defaults
            if fn is object.__init__:
                return [], []

        elif _inspect.isfunction(fn):
            nskip = 0

        elif _inspect.ismethod(fn):
            nskip = 1
            ## # bound method?
            ## if fn.im_self is None:
            ##     nskip = 0
            ## else:
            ##     nskip = 1
        else:
            raise TypeError('calllib unsupported type %r' % fn)

    # inspect the ultimate callable to find defaults
    argspec = _inspect.getargspec(fn)
    return argspec.args[nskip:], [] if argspec.defaults is None else argspec.defaults


def inspect_params(callable):
    """Given a callable object `callable`, return a tuple containing a
       list of parameters and a dict of default values."""

    param_names, defaults = _get_callable_info(callable)
    return param_names, {name: value for name, value in _zip(param_names[-len(defaults):], defaults)}


def getargs(callable, args):
    """Given a callable object `callable`, and a mapping of arguments
       `args`, return a list of actual arguments for
       `callable`. Handles default arguments that are not in args."""

    arg_names, defaults = _get_callable_info(callable)

    return [_get_arg(args, arg_name, n, len(arg_names), defaults)
            for n, arg_name in enumerate(arg_names)]


def apply(callable, args):
    """Given a callable object `callable`, and a mapping of arguments
       `args`, call `callable` with arguments taken from `args`. The
       arguments are found by matching argument names from the values
       in `args`."""

    return callable(*getargs(callable, args))
