# -*- coding: utf-8 -*-
"""
======================================================================
Collection of helper functions and misc tools (:mod:`pksci.tools`)
======================================================================

..currentmodule:: pksci.tools

Content
========

Array helper functions
-----------------------
.. autosummary::
   :toctree: generated/

   array_limits
   array_range
   resize_array
   resize_matrix

Functions for file I/O
------------------------
.. autosummary::
   :toctree: generated/

   get_fpath


Linear algebra functions for transformation operations
-------------------------------------------------------
.. autosummary::
   :toctree: generated/

   rotation_matrix

Math symbol-operator mappings
------------------------------

.. autosummary::
   :toctree: generated/

   comparison_symbol_operator_mappings
   math_symbol_operator_mappings
   symbol_operator_mappings

Math functions
---------------

.. autosummary::
   :toctree: generated/

   nextpow2
   nextpowb
   num2nextpow2
   num2nextpowb
   round2nearestN
   rounddown2nearestN
   roundup2nearestN

Vectorized versions of functions
---------------------------------

.. autosummary::
   :toctree: generated/

   vnextpow2
   vnextpowb
   vnum2nextpow2
   vnum2nextpowb
   vround2nearestN
   vrounddown2nearestN
   vroundup2nearestN

Helper functions for string manipulation
-----------------------------------------
.. autosummary::
   :toctree: generated/

   concat_units
   plural_word_check
   split_replace


Sub-packages
============
.. autosummary::
   :toctree: generated/

   datautils
   mpltools
   refdata

"""
from __future__ import division, print_function, absolute_import

from ._arrayfuncs import *
from ._fiofuncs import *
from ._mathfuncs import *
from ._strfuncs import *
from ._transforms import *

__all__ = [s for s in dir() if not s.startswith('_')]
