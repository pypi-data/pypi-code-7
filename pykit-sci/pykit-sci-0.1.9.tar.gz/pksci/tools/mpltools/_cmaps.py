# -*- coding: utf-8 -*-
"""
===========================================================================
Custom color maps (:mod:`pksci.tools.mpltools._cmaps`)
===========================================================================

.. currentmodule:: pksci.tools.refdata._cmaps

"""
from __future__ import division, absolute_import, print_function
__docformat__ = 'restructuredtext'

import matplotlib as mpl

__all__ = ['COLORS', 'CustomColormap']

COLORS = {}
#COLOR_MAPS = {}

#_BlYlGr_dict = {'red': ((0.0, 51 / 255, 51 / 255),
#                        (0.2, 180 / 255, 180 / 255),
#                        (0.4, 175 / 255, 175 / 255),
#                        (0.6, 206 / 255, 206 / 255),
#                        (0.8, 0 / 255, 0 / 255),
#                        (1.0, 102 / 255, 102 / 255)),
#                'green': ((0.0, 51 / 255, 51 / 255),
#                          (0.2, 180 / 255, 180 / 255),
#                          (0.4, 200 / 255, 200 / 255),
#                          (0.6, 211 / 255, 211 / 255),
#                          (0.8, 130 / 255, 130 / 255),
#                          (1.0, 217 / 255, 217 / 255)),
#                'blue': ((0.0, 51 / 255, 51 / 255),
#                         (0.2, 180 / 255, 180 / 255),
#                         (0.4, 7 / 255, 7 / 255),
#                         (0.6, 106 / 255, 106 / 255),
#                         (0.8, 195 / 255, 195 / 255),
#                         (1.0, 237 / 255, 237 / 255))}

_BlYlGr_list = ['#333333', '#B4B4B4', '#AFC807',
                '#CED36A', '#0082C3', '#66D9ED']

COLORS['BlYlGr'] = _BlYlGr_list
#_BlYlGr_cmap = \
#    mpl.colors.LinearSegmentedColormap.from_list('BlYlGr', _BlYlGr_list)
#
#COLOR_MAPS['BlYlGr'] = _BlYlGr_cmap

_BlGnOr_list = ['#0000FF', '#0055FF', '#00AAFF', '#00FFFF', '#55FFAA',
                '#AAFF55', '#FFFF00', '#FFAA00', '#FF5500']
COLORS['BlGnOr'] = _BlGnOr_list

_Jet2_list = ['#0000FF', '#0055FF', '#00AAFF', '#00FFFF', '#55FFAA',
              '#AAFF55', '#FFFF00', '#FFAA00', '#FF5500', '#FE1400']
COLORS['Jet2'] = _Jet2_list

#_BlGnOr_cmap = \
#    mpl.colors.LinearSegmentedColormap.from_list('BlGnOr', _BlGnOr_list)
#
#COLOR_MAPS['BlGnOr'] = _BlGnOr_cmap


class CustomColormap(object):

    def __init__(self, name, reverse=False):
        try:
            self._color_list = COLORS[name]
        except KeyError:
            s = 'Invalid color map name: {}\n'.format(name)
            s += 'Valid names are: {}'.format(sorted(COLORS.keys()))
            raise KeyError(s)

        self._name = name
        if reverse:
            self._color_list = [c for c in reversed(self._color_list)]

    def get_mpl_colormap(self, N=256, gamma=1.0):
        cmap = mpl.colors.LinearSegmentedColormap.from_list(self._name,
                                                            self._color_list,
                                                            N=N, gamma=gamma)
        return cmap
