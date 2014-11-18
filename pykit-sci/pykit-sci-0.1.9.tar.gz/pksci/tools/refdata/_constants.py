# -*- coding: utf-8 -*-
"""
=========================================================
Reference data (:mod:`pksci.tools.refdata._constants`)
=========================================================

Collection of physical constants and conversion factors
built upon :mod:`scipy.constants` module.

.. currentmodule:: pksci.tools.refdata._constants

"""
from __future__ import division, print_function, absolute_import
from scipy.constants import codata
from scipy.constants.constants import nano

h = codata.value('Planck constant in eV s')
c = codata.value('speed of light in vacuum')
hc = h * c / nano

C_C = CCbond = 1.421  # angstroms
C_H = CHbond = 1.09  # angstroms

__all__ = ['h', 'c', 'hc',
           'C_C', 'CCbond',
           'C_H', 'CHbond']
