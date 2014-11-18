# -*- coding: utf-8 -*-
"""
=========================================================================
Functions and tools for data analysis (:mod:`pksci.tools.datautils`)
=========================================================================

.. currentmodule:: pksci.tools.datautils

Contents
========

Abstract data structures for handling data
-------------------------------------------

.. autosummary::
   :toctree: generated/

   DataSet
   DataGroup

Data Logging
------------

.. autosummary::
   :toctree: generated/

   TextLogGenerator

Data Analysis
-------------

.. autosummary::
   :toctree: generated/

   error_bars
   line_eval
   line_fit_residuals
   normalize
   reblock_data
   smooth_data

Helper Functions
----------------

.. autosummary::
   :toctree: generated/

   generate_sequence
   inv_map
   load_data
   load_fixed_width_data

Custom exception classes for handling errors
---------------------------------------------

.. autosummary::
   :toctree: generated/

   LogGeneratorError

"""
from __future__ import division, print_function, absolute_import

__docformat__ = 'restructuredtext'

from ._data_analysis import *
from ._datafuncs import *
from ._dataset import *
from ._loggenerator import *

__all__ = [s for s in dir() if not s.startswith('_')]
