# -*- coding: utf-8 -*-
"""
============================================================
Functions for nanotubes (:mod:`pksci.nanosci._nanotubes`)
============================================================

.. currentmodule:: pksci.nanosci._nanotubes

"""
from __future__ import absolute_import, division, print_function

__docformat__ = 'restructuredtext'


__all__ = []


def Eii(p, dt):
    pass


def kataura_plot():
    pass


def rbm_freq(dt, etype=None, eqn=None):

    if etype is None and eqn is None:
        return 227 / dt
    if etype == 'semiconducting':
        A = 227
        B = 7.3
        C = -1.1
        D = -0.9
