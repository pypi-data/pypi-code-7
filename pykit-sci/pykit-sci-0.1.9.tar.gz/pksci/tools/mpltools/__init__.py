# -*- coding: utf-8 -*-
"""
=========================================================================
Modules for matplotlib plots (:mod:`pksci.tools.mpltools`)
=========================================================================

.. currentmodule:: pksci.tools.mpltools

Contents
========

Classes for parsing plot config files
-------------------------------------

.. autosummary::
   :toctree: generated/

   PlotConfig
   PlotConfigParser
   XYPlotConfigParser

Classes for generating plots
----------------------------

.. autosummary::
   :toctree: generated/

   PlotGenerator
   XYPlotGenerator
   MPLPlot
   XYPlot
   XYGridPlot

Custom exception classes for handling errors
---------------------------------------------

.. autosummary::
   :toctree: generated/

   PlotConfigParserError

Classes for custom plot filter effects and helper functions
-----------------------------------------------------------

.. autosummary::
   :toctree: generated/

   BaseFilter
   DropShadowFilter
   FilteredArtistList
   GaussianFilter
   GrowFilter
   LightFilter
   OffsetFilter

   plot_arrow_line
   drop_shadow_patches
   filtered_text
   light_filter_pie
   plot_dropshadow
   smooth1d
   smooth2d

Custom plot settings and helper functions
-----------------------------------------

.. autosummary::
   :toctree: generated/

   generate_axis_label_dict
   concat_units
   concat_y_vs_x
   get_mpl_rcParams
   plotstr
   replace_whitespace
   cmap_argparser
   plot_argparser

   color_dict
   marker_dict
   markersize_dict
   mpl_colors
   named_colors
   rainbow_color_list
   emacs_colors
   web_colors

Custom string presets and helper functions for text/LaTeX string manipulation
-----------------------------------------------------------------------------

.. autosummary::
   :toctree: generated/

   mathrm
   mathrm2mathsf
   mathsf
   mathsf2mathrm
   mixedstr2texstr
   texstr
   texstr2mathrm
   texstr2mathsf
   texstr2mathstr
   txt2tex
   txtstr2mathrm
   txtstr2mathsf
   txtstr2mathstr
   txtstr2texstr

   axis_texlabels
   axis_txtlabels
   var_equations
   var_texstrings
   var_texunits
   var_txtstrings
   var_txtunits

Custom color maps
--------------------

.. autosummary::
   :toctree: generated/

   COLORS
   CustomColormap

"""
from __future__ import absolute_import, division, print_function

__docformat__ = 'restructuredtext'

try:
    from ._argparser import *
    from ._cmaps import *
    from ._filters import *
    from ._luts import *
    from ._plotcfgparser import *
    from ._plotfuncs import *
    from ._plotgenerator import *
    from ._profiles import *
    from ._strings import *
except ImportError:
    print('`matplotlib` module not found. Install matplotlib 1.3+')

__all__ = [s for s in dir() if not s.startswith('_')]
