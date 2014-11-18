# -*- coding: utf-8 -*-
"""
===========================================================
Math functions (:mod:`pksci.tools._mathfuncs`)
===========================================================

.. currentmodule:: pksci.tools._mathfuncs

"""
from __future__ import division, print_function, absolute_import

import operator

import numpy as np

__all__ = ['nextpow2', 'nextpowb', 'num2nextpow2', 'num2nextpowb',
           'round2nearestN', 'rounddown2nearestN', 'roundup2nearestN',
           're_num', 'comparison_symbol_operator_mappings',
           'math_symbol_operator_mappings', 'symbol_operator_mappings',
           'vnextpow2', 'vnextpowb', 'vnum2nextpow2', 'vnum2nextpowb',
           'vround2nearestN', 'vrounddown2nearestN', 'vroundup2nearestN']

re_num = r'[+\-]?(\d+(\.\d*)?|\d*\.\d+)([Ee][+\-]?\d+)?'

symbol_operator_mappings = {}

comparison_symbol_operator_mappings = \
    {'==': operator.eq,
     '!=': operator.ne,
     '<': operator.lt,
     '<=': operator.le,
     '>': operator.gt,
     '>=': operator.ge,
     'is': operator.is_,
     'is not': operator.is_not}
symbol_operator_mappings.update(comparison_symbol_operator_mappings)

math_symbol_operator_mappings = \
    {'+': operator.add,
     '-': operator.sub,
     '*': operator.mul,
     '/': operator.div}
symbol_operator_mappings.update(math_symbol_operator_mappings)


def nextpow2(n):
    """Find :math:`p` that satisfies :math:`2^p \\ge |n|`.

    Parameters
    ----------
    n : int or float

    Returns
    -------
    p : int
        the power of 2 satisfying :math:`2^p \\ge |n|`.

    """
    p = 0
    pow2 = 2**p
    while pow2 < abs(n):
        p = p + 1
        pow2 = 2**p
    return p
vnextpow2 = np.vectorize(nextpow2)


def nextpowb(b, n):
    """Find :math:`p` that satisfies :math:`b^p \\ge |n|`.

    Parameters
    ----------
    b : int or float
        the base of the power :math:`p`. That is, the base :math:`b` in
        :math:`b^p`.
    n : int or float
        the value with absolute value that :math:`b^p` must be greater than
        or equal to.

    Returns
    -------
    p : int or float
        the power of :math:`b` satisfying :math:`b^p \\ge |n|`.

    """
    p = 0
    powb = b**p
    while powb < abs(n):
        p = p + 1
        powb = b**p
    return p
vnextpowb = np.vectorize(nextpowb)


def num2nextpow2(n):
    """Find the number = :math:`2^p \\ge |n|`.

    Parameters
    ----------
    n : int or float
        the value with absolute value that :math:`2^p` must be greater than
        or equal to.

    Returns
    -------
    pow2 : int
        the power of 2 = :math:`2^p \\ge |n|`.

    """
    p = nextpow2(n)
    pow2 = 2**p
    return pow2
vnum2nextpow2 = np.vectorize(num2nextpow2)


def num2nextpowb(b, n):
    """Find the number = :math:`b^p \\ge |n|`.

    Parameters
    ----------
    b : int or float
        the base of the power. That is, the base :math:`b` in :math:`b^p`.
    n : int or float
        the value with absolute value that :math:`b^p` must be greater than
        or equal to.

    Returns
    -------
    powb : int or float
        the next evaluated power of :math:`b` satisfying
        :math:`b^p \\ge |n|`

    """
    p = nextpowb(b, n)
    powb = b**p
    return powb
vnum2nextpowb = np.vectorize(num2nextpowb)


def round2nearestN(x, N=1):
    """Round number :math:`x` to nearest :math:`N`.

    Parameters
    ----------
    x : int or float
        number to round.
    N : int or float
        number to round :math:`x` to.

    Returns
    -------
    int or float
        :math:`x` rounded to nearest :math:`N`.

    """
    if isinstance(N, (int, long)):
        return int(N * round(float(x) / N))
    else:
        return N * round(float(x) / N)
vround2nearestN = np.vectorize(round2nearestN)


def roundup2nearestN(x, N=1):
    """Round number :math:`x` up to nearest :math:`N`.

    Parameters
    ----------
    x : int or float
        number to round.
    N : int or float
        number to round :math:`x` up to.

    Returns
    -------
    int or float
        :math:`x` rounded up to nearest :math:`N`.

    """

    from math import ceil

    if isinstance(N, (int, long)):
        return int(N * ceil(float(x) / N))
    else:
        return N * ceil(float(x) / N)
vroundup2nearestN = np.vectorize(roundup2nearestN)


def rounddown2nearestN(x, N=1):
    """Round number :math:`x` down to nearest :math:`N`.

    Parameters
    ----------
    x : int or float
        number to round.
    N : int or float
        number to round :math:`x` down to.

    Returns
    -------
    int or float
        :math:`x` rounded down to nearest :math:`N`.

    """
    from math import floor

    if isinstance(N, (int, long)):
        return int(N * floor(float(x) / N))
    else:
        return N * floor(float(x) / N)
vrounddown2nearestN = np.vectorize(rounddown2nearestN)
