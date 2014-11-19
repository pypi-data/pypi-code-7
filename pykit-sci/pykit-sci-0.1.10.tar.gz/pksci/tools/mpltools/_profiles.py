# -*- coding: utf-8 -*-
"""
==================================================================
Plot profiles and tools (:mod:`pksci.tools.mpltools._profiles`)
==================================================================

.. currentmodule:: pksci.tools.mpltools._profiles

"""
from __future__ import absolute_import, division, print_function

__all__ = ['get_mpl_rcParams']


def get_mpl_rcParams(mplobj, profile=None, usetex=False,
                     fontfamily='sans-serif', aspectratio=None):
    """Set matplotlib rcParams dictionary with custom plot profile settings.

    Parameters
    ----------
    mplobj : py:mod:`matplotlib` module instance
    profile : str, optional
        custom plot profile settings to use.
    usetex : bool, optional
    fontfamily : {'sans-serif', 'serif'}, optional
    aspectratio : float, optional

    Returns
    -------
    figkwargs : dict

    """
    figkwargs = {}

    if fontfamily not in ('sans-serif', 'serif'):
        fontfamily = 'sans-serif'

    mplobj.rcParams['font.family'] = fontfamily

    if usetex:
        mplobj.rcParams['text.usetex'] = True
        if fontfamily == 'sans-serif':
            mplobj.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
            mplobj.rcParams['text.latex.preamble'] = \
                [r'\usepackage{sfmath,amsmath,amssymb,latexsym}']
        else:
            #mplobj.rcParams['font.serif'] = ['Times']
            mplobj.rcParams['text.latex.preamble'] = \
                [r'\usepackage{amsmath,amssymb,latexsym}']
    else:
        mplobj.rcParams['text.usetex'] = False
        if fontfamily == 'sans-serif':
            mplobj.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
            #mplobj.rcParams['text.latex.preamble'] = [r'\usepackage{sfmath}']

    if profile == 'custom':

        figkwargs['xdim'] = figkwargs['ydim'] = 20
        figkwargs['cbar.label.fontsize'] = 40
        figkwargs['contour.label.fontsize'] = 44
        figkwargs['annotation.fontsize'] = 20
        figkwargs['marker.scale.factor'] = 2
        figkwargs['legend.marker.scale.factor'] = 0.5
        figkwargs['labelpad'] = 20
        figkwargs['title.fontsize'] = 52
        figkwargs['text.label.fontsize'] = 42

        figkwargs['tick.width'] = 5
        figkwargs['tick.major.width'] = figkwargs['tick.width']
        figkwargs['tick.minor.width'] = figkwargs['tick.width']

        figkwargs['inset.axes.linewidth'] = 3
        figkwargs['inset.axes.markersize'] = 15
        figkwargs['inset.axes.fontsize'] = 32
        figkwargs['inset.axes.labelsize'] = 36
        figkwargs['inset.axes.labelpad'] = 10
        figkwargs['inset.axes.tick.major.size'] = 10
        figkwargs['inset.axes.tick.minor.size'] = 6
        figkwargs['inset.axes.tick.width'] = 3

        #mplobj.rcParams['axes.titlesize'] = 52
        mplobj.rcParams['font.family'] = 'serif'
        mplobj.rcParams['font.size'] = 48
        mplobj.rcParams['legend.fontsize'] = 46
        mplobj.rcParams['legend.labelspacing'] = 1
        mplobj.rcParams['axes.linewidth'] = 5.0
        mplobj.rcParams['lines.linewidth'] = 6.0
        mplobj.rcParams['lines.markersize'] = 25

        mplobj.rcParams['xtick.major.size'] = 20
        mplobj.rcParams['xtick.minor.size'] = 10
        mplobj.rcParams['xtick.major.width'] = 5
        mplobj.rcParams['xtick.minor.width'] = 5
        mplobj.rcParams['xtick.major.pad'] = 12
        mplobj.rcParams['xtick.minor.pad'] = 12

        mplobj.rcParams['ytick.major.size'] = 20
        mplobj.rcParams['ytick.minor.size'] = 10
        mplobj.rcParams['ytick.major.width'] = 5
        mplobj.rcParams['ytick.minor.width'] = 5
        mplobj.rcParams['ytick.major.pad'] = 12
        mplobj.rcParams['ytick.minor.pad'] = 12

    elif profile == 'ipynb-inline':

        figkwargs['xdim'] = figkwargs['ydim'] = 12

        figkwargs['cbar.label.fontsize'] = 14
        figkwargs['contour.label.fontsize'] = 20
        figkwargs['annotation.fontsize'] = 12
        figkwargs['tiny.annotation.fontsize'] = 8
        figkwargs['text.fontsize'] = 5
        figkwargs['tiny.text.fontsize'] = 3
        figkwargs['marker.scale.factor'] = 1
        figkwargs['labelpad'] = 5
        figkwargs['legend.marker.scale.factor'] = 1
        figkwargs['legend.fontsize'] = 20
        figkwargs['title.fontsize'] = 20
        figkwargs['dropshadow.offset.x'] = 3
        figkwargs['dropshadow.offset.y'] = -6
        figkwargs['text.label.fontsize'] = 20

        figkwargs['tick.major.size'] = 12
        figkwargs['tick.minor.size'] = 6

        figkwargs['tick.width'] = 2
        figkwargs['tick.major.width'] = figkwargs['tick.width']
        figkwargs['tick.minor.width'] = figkwargs['tick.width']

        figkwargs['inset.axes.linewidth'] = 1
        figkwargs['inset.axes.markersize'] = 8
        figkwargs['inset.axes.marker.scale.factor'] = 0.5
        figkwargs['inset.axes.fontsize'] = 16
        figkwargs['inset.axes.labelsize'] = 16
        figkwargs['inset.axes.labelpad'] = 1
        figkwargs['inset.axes.legend.fontsize'] = 8
        figkwargs['inset.axes.annotation.fontsize'] = 12
        figkwargs['inset.axes.tiny.annotation.fontsize'] = 3
        figkwargs['inset.axes.text.fontsize'] = 4
        figkwargs['inset.axes.tiny.text.fontsize'] = 3
        figkwargs['inset.axes.tick.major.size'] = 6
        figkwargs['inset.axes.tick.minor.size'] = 3
        figkwargs['inset.axes.tick.width'] = 1
        figkwargs['inset.axes.tick.labelsize'] = 16
        figkwargs['inset.axes.tick.labelpad'] = 0.3

        mplobj.rcParams['font.size'] = 24
        mplobj.rcParams['axes.labelsize'] = 28
        mplobj.rcParams['legend.fontsize'] = 22

        mplobj.rcParams['legend.borderpad'] = 0.5
        mplobj.rcParams['legend.markerscale'] = 1.0
        mplobj.rcParams['legend.labelspacing'] = 0.25
        mplobj.rcParams['legend.handlelength'] = 1.25
        mplobj.rcParams['legend.handleheight'] = 1.0
        mplobj.rcParams['legend.handletextpad'] = 0.25
        mplobj.rcParams['legend.borderaxespad'] = 0.125
        mplobj.rcParams['axes.linewidth'] = 2
        mplobj.rcParams['lines.linewidth'] = 3
        mplobj.rcParams['lines.markersize'] = 8
        mplobj.rcParams['lines.markeredgewidth'] = 1.5

        mplobj.rcParams['xtick.direction'] = 'out'
        mplobj.rcParams['xtick.major.size'] = 12
        mplobj.rcParams['xtick.minor.size'] = 6
        mplobj.rcParams['xtick.major.width'] = 2
        mplobj.rcParams['xtick.minor.width'] = 2
        mplobj.rcParams['xtick.major.pad'] = 4
        mplobj.rcParams['xtick.minor.pad'] = 4

        mplobj.rcParams['ytick.direction'] = 'out'
        mplobj.rcParams['ytick.major.size'] = 12
        mplobj.rcParams['ytick.minor.size'] = 6
        mplobj.rcParams['ytick.major.width'] = 2
        mplobj.rcParams['ytick.minor.width'] = 2
        mplobj.rcParams['ytick.major.pad'] = 4
        mplobj.rcParams['ytick.minor.pad'] = 4

    elif profile == 'kgraph':

        figkwargs['xdim'] = figkwargs['ydim'] = 4

        figkwargs['cbar.label.fontsize'] = 7
        figkwargs['contour.label.fontsize'] = 10
        figkwargs['annotation.fontsize'] = 6
        figkwargs['tiny.annotation.fontsize'] = 4
        figkwargs['text.fontsize'] = 2.5
        figkwargs['tiny.text.fontsize'] = 1.5
        figkwargs['marker.scale.factor'] = 0.3
        figkwargs['labelpad'] = 2.5
        figkwargs['legend.marker.scale.factor'] = 1.0
        figkwargs['legend.fontsize'] = 10.5
        figkwargs['title.fontsize'] = 10
        figkwargs['dropshadow.offset.x'] = 1.5
        figkwargs['dropshadow.offset.y'] = -3
        figkwargs['text.label.fontsize'] = 10

        figkwargs['tick.major.size'] = 6
        figkwargs['tick.minor.size'] = 3

        figkwargs['tick.width'] = 1
        figkwargs['tick.major.width'] = figkwargs['tick.width']
        figkwargs['tick.minor.width'] = figkwargs['tick.width']

        figkwargs['inset.axes.linewidth'] = 0.5
        figkwargs['inset.axes.markersize'] = 4
        figkwargs['inset.axes.marker.scale.factor'] = 0.25
        figkwargs['inset.axes.fontsize'] = 6
        figkwargs['inset.axes.labelsize'] = 7
        figkwargs['inset.axes.labelpad'] = 0.5
        figkwargs['inset.axes.legend.fontsize'] = 4
        figkwargs['inset.axes.annotation.fontsize'] = 6
        figkwargs['inset.axes.tiny.annotation.fontsize'] = 1.5
        figkwargs['inset.axes.text.fontsize'] = 2
        figkwargs['inset.axes.tiny.text.fontsize'] = 1.5
        figkwargs['inset.axes.tick.major.size'] = 3
        figkwargs['inset.axes.tick.minor.size'] = 1.5
        figkwargs['inset.axes.tick.width'] = 0.5
        figkwargs['inset.axes.tick.labelsize'] = 5
        figkwargs['inset.axes.tick.labelpad'] = 0.15

        mplobj.rcParams['font.size'] = 12
        mplobj.rcParams['axes.labelsize'] = 14
        mplobj.rcParams['legend.fontsize'] = 12

        mplobj.rcParams['legend.borderpad'] = 0.5
        mplobj.rcParams['legend.markerscale'] = 1.0
        mplobj.rcParams['legend.labelspacing'] = 0.25
        mplobj.rcParams['legend.handlelength'] = 1.25
        mplobj.rcParams['legend.handleheight'] = 1.0
        mplobj.rcParams['legend.handletextpad'] = 0.25
        mplobj.rcParams['legend.borderaxespad'] = 0.5
        mplobj.rcParams['axes.linewidth'] = 1
        mplobj.rcParams['lines.linewidth'] = 1.5
        mplobj.rcParams['lines.markersize'] = 4.0
        mplobj.rcParams['lines.markeredgewidth'] = 0.75

        mplobj.rcParams['xtick.direction'] = 'out'
        mplobj.rcParams['xtick.major.size'] = 6
        mplobj.rcParams['xtick.minor.size'] = 3
        mplobj.rcParams['xtick.major.width'] = 1
        mplobj.rcParams['xtick.minor.width'] = 1
        mplobj.rcParams['xtick.major.pad'] = 2
        mplobj.rcParams['xtick.minor.pad'] = 2

        mplobj.rcParams['ytick.direction'] = 'out'
        mplobj.rcParams['ytick.major.size'] = 6
        mplobj.rcParams['ytick.minor.size'] = 3
        mplobj.rcParams['ytick.major.width'] = 1
        mplobj.rcParams['ytick.minor.width'] = 1
        mplobj.rcParams['ytick.major.pad'] = 2.5
        mplobj.rcParams['ytick.minor.pad'] = 2.5

    elif profile == 'kgraph-wide':

        figkwargs['xdim'] = 12
        figkwargs['ydim'] = 3

        figkwargs['cbar.label.fontsize'] = 7
        figkwargs['contour.label.fontsize'] = 10
        figkwargs['annotation.fontsize'] = 6
        figkwargs['tiny.annotation.fontsize'] = 4
        figkwargs['text.fontsize'] = 2.5
        figkwargs['tiny.text.fontsize'] = 1.5
        figkwargs['marker.scale.factor'] = 0.3
        figkwargs['labelpad'] = 4
        figkwargs['legend.marker.scale.factor'] = 1.0
        figkwargs['legend.fontsize'] = 10.5
        figkwargs['title.fontsize'] = 10
        figkwargs['dropshadow.offset.x'] = 1.5
        figkwargs['dropshadow.offset.y'] = -3
        figkwargs['text.label.fontsize'] = 10

        figkwargs['tick.major.size'] = 6
        figkwargs['tick.minor.size'] = 3

        figkwargs['tick.width'] = 1
        figkwargs['tick.major.width'] = figkwargs['tick.width']
        figkwargs['tick.minor.width'] = figkwargs['tick.width']

        figkwargs['inset.axes.linewidth'] = 1
        figkwargs['inset.axes.markersize'] = 4
        figkwargs['inset.axes.marker.scale.factor'] = 0.25
        figkwargs['inset.axes.fontsize'] = 6
        figkwargs['inset.axes.labelsize'] = 7
        figkwargs['inset.axes.labelpad'] = 0.5
        figkwargs['inset.axes.legend.fontsize'] = 4
        figkwargs['inset.axes.annotation.fontsize'] = 6
        figkwargs['inset.axes.tiny.annotation.fontsize'] = 1.5
        figkwargs['inset.axes.text.fontsize'] = 2
        figkwargs['inset.axes.tiny.text.fontsize'] = 1.5
        figkwargs['inset.axes.tick.major.size'] = 3
        figkwargs['inset.axes.tick.minor.size'] = 1.5
        figkwargs['inset.axes.tick.width'] = 0.5
        figkwargs['inset.axes.tick.labelsize'] = 5
        figkwargs['inset.axes.tick.labelpad'] = 0.15

        mplobj.rcParams['font.size'] = 16
        mplobj.rcParams['axes.labelsize'] = 18
        mplobj.rcParams['legend.fontsize'] = 16

        mplobj.rcParams['legend.borderpad'] = 0.5
        mplobj.rcParams['legend.markerscale'] = 1.0
        mplobj.rcParams['legend.labelspacing'] = 0.25
        mplobj.rcParams['legend.handlelength'] = 1.25
        mplobj.rcParams['legend.handleheight'] = 1.0
        mplobj.rcParams['legend.handletextpad'] = 0.25
        mplobj.rcParams['legend.borderaxespad'] = 0.125
        mplobj.rcParams['axes.linewidth'] = 2
        mplobj.rcParams['lines.linewidth'] = 3
        mplobj.rcParams['lines.markersize'] = 4.0
        mplobj.rcParams['lines.markeredgewidth'] = 0.75

        mplobj.rcParams['xtick.direction'] = 'out'
        mplobj.rcParams['xtick.major.size'] = 7
        mplobj.rcParams['xtick.minor.size'] = 4
        mplobj.rcParams['xtick.major.width'] = 2
        mplobj.rcParams['xtick.minor.width'] = 2
        mplobj.rcParams['xtick.major.pad'] = 4
        mplobj.rcParams['xtick.minor.pad'] = 4

        mplobj.rcParams['ytick.direction'] = 'out'
        mplobj.rcParams['ytick.major.size'] = 7
        mplobj.rcParams['ytick.minor.size'] = 4
        mplobj.rcParams['ytick.major.width'] = 2
        mplobj.rcParams['ytick.minor.width'] = 2
        mplobj.rcParams['ytick.major.pad'] = 4
        mplobj.rcParams['ytick.minor.pad'] = 4

    elif profile == 'paper':

        figkwargs['xdim'] = figkwargs['ydim'] = 4
        figkwargs['cbar.label.fontsize'] = 7
        figkwargs['contour.label.fontsize'] = 10
        figkwargs['annotation.fontsize'] = 3
        figkwargs['ax.annotation.fontsize'] = 3
        figkwargs['text.fontsize'] = 3
        figkwargs['tiny.text.fontsize'] = 1.5
        figkwargs['marker.scale.factor'] = 0.3
        figkwargs['labelpad'] = 3
        figkwargs['legend.marker.scale.factor'] = 1.0
        figkwargs['legend.fontsize'] = 4
        figkwargs['title.fontsize'] = 10
        figkwargs['dropshadow.offset.x'] = 1.5
        figkwargs['dropshadow.offset.y'] = -3
        figkwargs['text.label.fontsize'] = 10

        figkwargs['tick.major.size'] = 4
        figkwargs['tick.minor.size'] = 2

        figkwargs['tick.width'] = 1
        figkwargs['tick.major.width'] = figkwargs['tick.width']
        figkwargs['tick.minor.width'] = figkwargs['tick.width']

        figkwargs['inset.axes.linewidth'] = 1
        figkwargs['inset.axes.markersize'] = 2
        figkwargs['inset.axes.marker.scale.factor'] = 0.2
        figkwargs['inset.axes.fontsize'] = 4
        figkwargs['inset.axes.labelsize'] = 6
        figkwargs['inset.axes.labelpad'] = 1.5
        figkwargs['inset.axes.annotation.fontsize'] = 6
        figkwargs['inset.axes.tiny.annotation.fontsize'] = 1.5
        figkwargs['inset.axes.text.fontsize'] = 6
        figkwargs['inset.axes.tiny.text.fontsize'] = 1.5
        figkwargs['inset.axes.legend.fontsize'] = 3
        figkwargs['inset.axes.tick.major.size'] = 2.5
        figkwargs['inset.axes.tick.minor.size'] = 1.5
        figkwargs['inset.axes.tick.width'] = .75
        figkwargs['inset.axes.tick.labelsize'] = 5
        figkwargs['inset.axes.tick.labelpad'] = 0.25

        mplobj.rcParams['font.size'] = 10
        mplobj.rcParams['axes.labelsize'] = 12
        mplobj.rcParams['legend.fontsize'] = 6
        mplobj.rcParams['legend.labelspacing'] = 0.4
        mplobj.rcParams['axes.linewidth'] = 1
        mplobj.rcParams['lines.linewidth'] = 1.5
        mplobj.rcParams['lines.markersize'] = 4.0
        mplobj.rcParams['lines.markeredgewidth'] = 0.75

        mplobj.rcParams['xtick.major.size'] = 4
        mplobj.rcParams['xtick.minor.size'] = 2
        mplobj.rcParams['xtick.major.width'] = 1
        mplobj.rcParams['xtick.minor.width'] = 1
        mplobj.rcParams['xtick.major.pad'] = 2
        mplobj.rcParams['xtick.minor.pad'] = 2

        mplobj.rcParams['ytick.major.size'] = 4
        mplobj.rcParams['ytick.minor.size'] = 2
        mplobj.rcParams['ytick.major.width'] = 1
        mplobj.rcParams['ytick.minor.width'] = 1
        mplobj.rcParams['ytick.major.pad'] = 2
        mplobj.rcParams['ytick.minor.pad'] = 2

    elif profile in ('2-col', '2-column', 'double-column'):

        figkwargs['xdim'] = figkwargs['ydim'] = 8

        figkwargs['cbar.label.fontsize'] = 14
        figkwargs['contour.label.fontsize'] = 20
        figkwargs['annotation.fontsize'] = 12
        figkwargs['tiny.annotation.fontsize'] = 8
        figkwargs['text.fontsize'] = 5
        figkwargs['tiny.text.fontsize'] = 3
        figkwargs['marker.scale.factor'] = 0.6
        figkwargs['labelpad'] = 5
        figkwargs['legend.marker.scale.factor'] = 1.0
        figkwargs['legend.fontsize'] = 21
        figkwargs['title.fontsize'] = 20
        figkwargs['dropshadow.offset.x'] = 3
        figkwargs['dropshadow.offset.y'] = -6
        figkwargs['text.label.fontsize'] = 20

        figkwargs['tick.major.size'] = 12
        figkwargs['tick.minor.size'] = 6

        figkwargs['tick.width'] = 2
        figkwargs['tick.major.width'] = figkwargs['tick.width']
        figkwargs['tick.minor.width'] = figkwargs['tick.width']

        figkwargs['inset.axes.linewidth'] = 1
        figkwargs['inset.axes.markersize'] = 8
        figkwargs['inset.axes.marker.scale.factor'] = 0.5
        figkwargs['inset.axes.fontsize'] = 12
        figkwargs['inset.axes.labelsize'] = 14
        figkwargs['inset.axes.labelpad'] = 1
        figkwargs['inset.axes.legend.fontsize'] = 8
        figkwargs['inset.axes.annotation.fontsize'] = 12
        figkwargs['inset.axes.tiny.annotation.fontsize'] = 3
        figkwargs['inset.axes.text.fontsize'] = 4
        figkwargs['inset.axes.tiny.text.fontsize'] = 3
        figkwargs['inset.axes.tick.major.size'] = 6
        figkwargs['inset.axes.tick.minor.size'] = 3
        figkwargs['inset.axes.tick.width'] = 1
        figkwargs['inset.axes.tick.labelsize'] = 10
        figkwargs['inset.axes.tick.labelpad'] = 0.3

        mplobj.rcParams['font.size'] = 24
        mplobj.rcParams['axes.labelsize'] = 28
        mplobj.rcParams['legend.fontsize'] = 24

        mplobj.rcParams['legend.borderpad'] = 0.5
        mplobj.rcParams['legend.markerscale'] = 1
        mplobj.rcParams['legend.labelspacing'] = 0.25
        mplobj.rcParams['legend.handlelength'] = 1.25
        mplobj.rcParams['legend.handleheight'] = 1
        mplobj.rcParams['legend.handletextpad'] = 0.25
        mplobj.rcParams['legend.borderaxespad'] = 0.125
        mplobj.rcParams['axes.linewidth'] = 2
        mplobj.rcParams['lines.linewidth'] = 3
        mplobj.rcParams['lines.markersize'] = 8
        mplobj.rcParams['lines.markeredgewidth'] = 1.5

        mplobj.rcParams['xtick.direction'] = 'out'
        mplobj.rcParams['xtick.major.size'] = 10
        mplobj.rcParams['xtick.minor.size'] = 5
        mplobj.rcParams['xtick.major.width'] = 2
        mplobj.rcParams['xtick.minor.width'] = 2
        mplobj.rcParams['xtick.major.pad'] = 4
        mplobj.rcParams['xtick.minor.pad'] = 4

        mplobj.rcParams['ytick.direction'] = 'out'
        mplobj.rcParams['ytick.major.size'] = 10
        mplobj.rcParams['ytick.minor.size'] = 5
        mplobj.rcParams['ytick.major.width'] = 2
        mplobj.rcParams['ytick.minor.width'] = 2
        mplobj.rcParams['ytick.major.pad'] = 4
        mplobj.rcParams['ytick.minor.pad'] = 4

    elif profile == 'tiny':

        figkwargs['xdim'] = figkwargs['ydim'] = 2
        figkwargs['cbar.label.fontsize'] = 4
        figkwargs['contour.label.fontsize'] = 5
        figkwargs['annotation.fontsize'] = 1.5
        figkwargs['ax.annotation.fontsize'] = 1.5
        figkwargs['marker.scale.factor'] = 0.175
        figkwargs['legend.marker.scale.factor'] = 1.0
        figkwargs['legend.fontsize'] = 2
        figkwargs['labelpad'] = 1.5
        figkwargs['title.fontsize'] = 5
        figkwargs['dropshadow.offset.x'] = 0.75
        figkwargs['dropshadow.offset.y'] = -1.5
        figkwargs['text.label.fontsize'] = 6

        figkwargs['tick.major.size'] = 2
        figkwargs['tick.minor.size'] = 1

        figkwargs['tick.width'] = 0.5
        figkwargs['tick.major.width'] = figkwargs['tick.width']
        figkwargs['tick.minor.width'] = figkwargs['tick.width']

        figkwargs['inset.axes.linewidth'] = 0.5
        figkwargs['inset.axes.markersize'] = 1
        figkwargs['inset.axes.marker.scale.factor'] = 0.1
        figkwargs['inset.axes.fontsize'] = 2
        figkwargs['inset.axes.labelsize'] = 3
        figkwargs['inset.axes.labelpad'] = 0.75
        figkwargs['inset.axes.legend.fontsize'] = 1.5
        figkwargs['inset.axes.tick.major.size'] = 1.25
        figkwargs['inset.axes.tick.minor.size'] = 0.75
        figkwargs['inset.axes.tick.width'] = 0.375
        figkwargs['inset.axes.tick.labelsize'] = 2.5
        figkwargs['inset.axes.tick.labelpad'] = 0.125

        mplobj.rcParams['font.size'] = 5
        mplobj.rcParams['axes.labelsize'] = 7
        mplobj.rcParams['legend.fontsize'] = 3
        mplobj.rcParams['legend.labelspacing'] = 0.2
        mplobj.rcParams['axes.linewidth'] = 0.5
        mplobj.rcParams['lines.linewidth'] = 1.0
        mplobj.rcParams['lines.markersize'] = 2.0
        mplobj.rcParams['lines.markeredgewidth'] = 0.25

        mplobj.rcParams['xtick.major.size'] = 2
        mplobj.rcParams['xtick.minor.size'] = 1.25
        mplobj.rcParams['xtick.major.width'] = 0.5
        mplobj.rcParams['xtick.minor.width'] = 0.5
        mplobj.rcParams['xtick.major.pad'] = 1.25
        mplobj.rcParams['xtick.minor.pad'] = 1.25

        mplobj.rcParams['ytick.major.size'] = 2
        mplobj.rcParams['ytick.minor.size'] = 1.25
        mplobj.rcParams['ytick.major.width'] = 0.5
        mplobj.rcParams['ytick.minor.width'] = 0.5
        mplobj.rcParams['ytick.major.pad'] = 1.25
        mplobj.rcParams['ytick.minor.pad'] = 1.25

    elif profile == 'print':

        figkwargs['xdim'] = figkwargs['ydim'] = 10
        figkwargs['cbar.label.fontsize'] = 18
        figkwargs['contour.label.fontsize'] = 22
        figkwargs['annotation.fontsize'] = 10
        figkwargs['ax.annotation.fontsize'] = 8
        figkwargs['marker.scale.factor'] = 0.8
        figkwargs['labelpad'] = 10
        figkwargs['title.fontsize'] = 28
        figkwargs['legend.marker.scale.factor'] = .5
        figkwargs['legend.fontsize'] = 16
        figkwargs['dropshadow.offset.x'] = 4
        figkwargs['dropshadow.offset.y'] = -6
        figkwargs['text.label.fontsize'] = 20

        figkwargs['tick.major.size'] = 4
        figkwargs['tick.minor.size'] = 2
        figkwargs['tick.width'] = 1.5
        figkwargs['tick.major.width'] = figkwargs['tick.width']
        figkwargs['tick.minor.width'] = figkwargs['tick.width']

        figkwargs['inset.axes.linewidth'] = 1.5
        figkwargs['inset.axes.markersize'] = 8
        figkwargs['inset.axes.marker.scale.factor'] = 0.5
        figkwargs['inset.axes.fontsize'] = 10
        figkwargs['inset.axes.labelsize'] = 14
        figkwargs['inset.axes.labelpad'] = 3
        figkwargs['inset.axes.legend.fontsize'] = 8
        figkwargs['inset.axes.tick.major.size'] = 6
        figkwargs['inset.axes.tick.minor.size'] = 4
        figkwargs['inset.axes.tick.width'] = 1.5
        figkwargs['inset.axes.tick.labelsize'] = 12
        figkwargs['inset.axes.tick.labelpad'] = 1

        #mplobj.rcParams['font.family'] = 'sans-serif'
        mplobj.rcParams['font.size'] = 22
        mplobj.rcParams['axes.labelsize'] = 24
        mplobj.rcParams['legend.fontsize'] = 15
        mplobj.rcParams['legend.labelspacing'] = 0.4
        mplobj.rcParams['axes.linewidth'] = 2
        mplobj.rcParams['lines.linewidth'] = 3.0
        mplobj.rcParams['lines.markersize'] = 12.5
        mplobj.rcParams['lines.markeredgewidth'] = 1.0

        mplobj.rcParams['xtick.major.size'] = 10
        mplobj.rcParams['xtick.minor.size'] = 5
        mplobj.rcParams['xtick.major.width'] = 2
        mplobj.rcParams['xtick.minor.width'] = 2
        mplobj.rcParams['xtick.major.pad'] = 8
        mplobj.rcParams['xtick.minor.pad'] = 8

        mplobj.rcParams['ytick.major.size'] = 10
        mplobj.rcParams['ytick.minor.size'] = 5
        mplobj.rcParams['ytick.major.width'] = 2
        mplobj.rcParams['ytick.minor.width'] = 2
        mplobj.rcParams['ytick.major.pad'] = 8
        mplobj.rcParams['ytick.minor.pad'] = 8

    elif profile == 'poster':

        figkwargs['xdim'] = figkwargs['ydim'] = 20
        figkwargs['cbar.label.fontsize'] = 40
        figkwargs['contour.label.fontsize'] = 44
        figkwargs['annotation.fontsize'] = 20
        figkwargs['ax.annotation.fontsize'] = 14
        figkwargs['marker.scale.factor'] = 1
        figkwargs['legend.marker.scale.factor'] = 1
        figkwargs['legend.fontsize'] = 36
        figkwargs['labelpad'] = 20
        figkwargs['title.fontsize'] = 52
        figkwargs['text.label.fontsize'] = 42

        figkwargs['tick.major.size'] = 20
        figkwargs['tick.minor.size'] = 10
        figkwargs['tick.width'] = 5
        figkwargs['tick.major.width'] = figkwargs['tick.width']
        figkwargs['tick.minor.width'] = figkwargs['tick.width']

        figkwargs['inset.axes.linewidth'] = 3
        figkwargs['inset.axes.markersize'] = 15
        figkwargs['inset.axes.fontsize'] = 32
        figkwargs['inset.axes.labelsize'] = 36
        figkwargs['inset.axes.labelpad'] = 10
        figkwargs['inset.axes.tick.major.size'] = 10
        figkwargs['inset.axes.tick.minor.size'] = 6
        figkwargs['inset.axes.tick.width'] = 3

        mplobj.rcParams['font.family'] = 'sans-serif'
        mplobj.rcParams['font.size'] = 48
        mplobj.rcParams['axes.labelsize'] = 50
        mplobj.rcParams['legend.fontsize'] = 36
        mplobj.rcParams['legend.labelspacing'] = 0.4
        mplobj.rcParams['axes.linewidth'] = 5.0
        mplobj.rcParams['lines.linewidth'] = 6.0
        mplobj.rcParams['lines.markersize'] = 25
        mplobj.rcParams['lines.markeredgewidth'] = 3.0

        mplobj.rcParams['xtick.major.size'] = 20
        mplobj.rcParams['xtick.minor.size'] = 10
        mplobj.rcParams['xtick.major.width'] = 5
        mplobj.rcParams['xtick.minor.width'] = 5
        mplobj.rcParams['xtick.major.pad'] = 12
        mplobj.rcParams['xtick.minor.pad'] = 12

        mplobj.rcParams['ytick.major.size'] = 20
        mplobj.rcParams['ytick.minor.size'] = 10
        mplobj.rcParams['ytick.major.width'] = 5
        mplobj.rcParams['ytick.minor.width'] = 5
        mplobj.rcParams['ytick.major.pad'] = 12
        mplobj.rcParams['ytick.minor.pad'] = 12

    else:

        figkwargs['xdim'] = figkwargs['ydim'] = 8
        figkwargs['cbar.label.fontsize'] = 12
        figkwargs['contour.label.fontsize'] = 12
        figkwargs['annotation.fontsize'] = 10
        figkwargs['marker.scale.factor'] = 0.2
        figkwargs['legend.marker.scale.factor'] = 1
        figkwargs['labelpad'] = 5
        figkwargs['title.fontsize'] = 12
        figkwargs['text.label.fontsize'] = 12

        figkwargs['inset.axes.linewidth'] = 1
        figkwargs['inset.axes.markersize'] = 1
        figkwargs['inset.axes.fontsize'] = 8
        figkwargs['inset.axes.labelsize'] = 10
        figkwargs['inset.axes.labelpad'] = 2
        figkwargs['inset.axes.tick.major.size'] = 3
        figkwargs['inset.axes.tick.minor.size'] = 1
        figkwargs['inset.axes.tick.width'] = 1

        mplobj.rcParams['font.size'] = 12
        mplobj.rcParams['axes.labelsize'] = 14
        mplobj.rcParams['legend.fontsize'] = 12
        mplobj.rcParams['legend.labelspacing'] = 0.8
        mplobj.rcParams['axes.linewidth'] = 1.0
        mplobj.rcParams['lines.linewidth'] = 1.0
        mplobj.rcParams['lines.markersize'] = 1.0

        mplobj.rcParams['xtick.minor.size'] = 2
        mplobj.rcParams['xtick.major.size'] = 4
        mplobj.rcParams['xtick.major.width'] = 2
        mplobj.rcParams['xtick.minor.width'] = 2
        mplobj.rcParams['xtick.major.pad'] = 3
        mplobj.rcParams['xtick.minor.pad'] = 3
        mplobj.rcParams['xtick.labelsize'] = 'small'

        mplobj.rcParams['ytick.major.size'] = 4
        mplobj.rcParams['ytick.minor.size'] = 2
        mplobj.rcParams['ytick.major.width'] = 2
        mplobj.rcParams['ytick.minor.width'] = 2
        mplobj.rcParams['ytick.major.pad'] = 3
        mplobj.rcParams['ytick.minor.pad'] = 3
        mplobj.rcParams['ytick.labelsize'] = 'small'

    if isinstance(aspectratio, (int, float)):
        #figkwargs['xdim'] *= aspectratio
        figkwargs['ydim'] /= aspectratio

    return figkwargs
