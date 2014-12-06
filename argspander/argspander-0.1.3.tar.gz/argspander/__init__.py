"""
Module that provides argument expansion of objects.

It was created to enable a sane way of entering arguments gathered from
argparse into your program, without the need to pass round an arguments object.
"""
# The MIT License (MIT)
#
# Copyright (c) 2014 Richard Lancaster
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import inspect


def expand(func):
    """Decorator that expands an object's attributes to fill a function's
    parameters

    The decorated function should be passed an object whose attributes share
    the names of the function's parameters. The objects attributes will be
    expanded into both positional and keyword parameters.
    Supports functions and class methods.

    Decorated function parameters:
        expand: keyword arg. True to activate object expansion,
            else the decorated function behaves normally

    Usage:
        >>> @expand
        ... def f(a, b, c):
        ...     print "a: %s, b: %s, c: %s" % (a, b, c)
        >>> f(3, 2, 1)
        a: 3, b: 2, c: 1
        >>> class Args():  # similar to the object return by argparse
        ...     a = 3
        ...     b = 2
        ...     c = 1
        >>>  f(Args(), expand=True)
        a: 3, b: 2, c: 1
    """

    def _inner(*args, **kwargs):
        func_varnames = inspect.getargspec(func).args

        if kwargs.get("expand") is True and func_varnames:
            func_args = []

            # deal with methods
            if func_varnames[0] is "self":
                func_args.append(args[0])
                args = args[1:]
                func_varnames = func_varnames[1:]

            func_args.extend(
                [getattr(args[0], varname) for varname in func_varnames]
            )

            return func(*func_args)

        else:
            return func(*args, **kwargs)

    return _inner
