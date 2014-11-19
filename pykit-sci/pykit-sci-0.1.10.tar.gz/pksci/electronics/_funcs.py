# -*- coding: utf-8 -*-
"""
============================================================
Functions for electronics (:mod:`pksci.electronics._funcs`)
============================================================

.. currentmodule:: pksci.electronics._funcs

"""
from __future__ import absolute_import, division, print_function
__docformat__ = 'restructuredtext en'

try:
    from pint import UnitRegistry
    ureg = UnitRegistry()
    Qty = ureg.Quantity
except ImportError:
    Qty = None

__all__ = ['compute_CLR']


def compute_CLR(Vf, Vi, i):
    return (Vf - Vi) / i
