# -*- coding: utf-8 -*-
"""
==============================================================================
argparser for plot scripts (:mod:`pksci.tools.mpltools._argparser`)
==============================================================================

.. currentmodule:: pksci.tools.mpltools._argparser

"""
from __future__ import division, print_function, absolute_import

import argparse
import os

__all__ = ['plot_argparser', 'cmap_argparser']


def plot_argparser():
    parser = argparse.ArgumentParser()
    plotargs = parser.add_argument_group('Plot arguments')
    plotargs.add_argument('--add-fig-ref', action='store_true',
                          help='add figure reference to top left corner')
    plotargs.add_argument('--add-zoomed-inset', action='store_true',
                          help='add zoomed inset axes to plot')
    plotargs.add_argument('--alpha', type=float, default=0.8,
                          help='alpha blending (transparency) value '
                          '(default: %(default)s)')
    plotargs.add_argument('--aspectratio', type=float, default=None,
                          help='aspect ratio of figure (default: %(default)s)')
    plotargs.add_argument('--bbox-inches', default='tight',
                          help="Bbox in inches. Only the given portion of the "
                          "figure is saved. If 'tight', try to figure out the "
                          "tight bbox of the figure (default: %(default)s).")
    plotargs.add_argument('--capsize', type=float, default=None,
                          help='set length of errorbar caps. '
                          '(default: %(default)s)')
    plotargs.add_argument('--capthick', type=float, default=None,
                          help='set thickness of errorbar caps. '
                          '(default: %(default)s)')
    plotargs.add_argument('--dalpha', type=float, default=0.01,
                          help='change in alpha blending (transparency) '
                          'value for plot overlays (default: %(default)s)')
    plotargs.add_argument('--disable-legend', action='store_true',
                          help='turn off legend')
    plotargs.add_argument('--disable-markers', action='store_true',
                          help='turn off plot markers')
    plotargs.add_argument('--disable-plotting', action='store_true',
                          help="Perform data analysis, but don't plot data.")
    plotargs.add_argument('--disable-savefig', action='store_true',
                          help='disable figure saving')
    plotargs.add_argument('--ecolor', type=float, default=None,
                          help='color of errorbar lines. If `None`, use the '
                          'marker color. (default: %(default)s)')
    plotargs.add_argument('--elinewidth', type=float, default=None,
                          help='linewidth of errorbar lines. '
                          '(default: %(default)s)')
    plotargs.add_argument('--enable-dropshadow', action='store_true',
                          help='enable dropshadow effect')
    plotargs.add_argument('--file-num', type=int, default=None,
                          help='starting file number (default: %(default)s)')
    plotargs.add_argument('--fontfamily', choices=('sans-serif', 'serif'),
                          default='sans-serif', help='font family '
                          '(default: %(default)s)')
    plotargs.add_argument('--fname-prefix', default=None,
                          help='prepend plot file name with this '
                          'prefix (default: %(default)s)')
    plotargs.add_argument('--fname-suffix', default=None,
                          help='append plot file name with this '
                          'suffix (default: %(default)s)')
    plotargs.add_argument('--legend-frameon', action='store_true',
                          help="if True, draw a frame around the legend.")
    plotargs.add_argument('--global-scale-factor', type=float, default=0.5,
                          help='scale plots markers by this factor'
                          '(default: %(default)s)')
    plotargs.add_argument('--inset-cfgfile', default=None,
                          help='configuration file specifying plot settings '
                          'for plot insets. (default: %(default)s)')
    plotargs.add_argument('--legend-fontsize', type=float, default=None,
                          help='legend fontsize (default: %(default)s)')
    plotargs.add_argument('--legend-ncol', type=int, default=1,
                          help='number of legend columns '
                          '(default: %(default)s)')
    plotargs.add_argument('--legend-loc', default='best',
                          choices=('best', 'upper right', 'upper left',
                                   'lower right', 'lower left'),
                          help='legend location (default: %(default)s)')
    plotargs.add_argument('--linewidth', type=float, default=0,
                          help='plot line width (default: %(default)s)')
    plotargs.add_argument('--markercolor', default=None,
                          help="plot marker color (default: %(default)s).")
    plotargs.add_argument('--markeredgewidth', type=float, default=None,
                          help='plot marker edge width '
                          '(default: %(default)s).')
    plotargs.add_argument('--markersize', type=float, default=3,
                          help='plot marker size (default: %(default)s). '
                          'Computed automatically and is non-zero unless '
                          '`--disable-markers` command line argument is '
                          'passed')
    plotargs.add_argument('--markevery', type=int, default=1,
                          help='plot marker every multiple of markevery '
                          '(default: %(default)s)')
    plotargs.add_argument('--ncols', type=int, default=None,
                          help='number of plot cols (default: %(default)s)')
    plotargs.add_argument('--nrows', type=int, default=None,
                          help='number of plot rows (default: %(default)s)')
    plotargs.add_argument('--outpath', default=os.getcwd(),
                          help='output path (default: %(default)s)')
    plotargs.add_argument('--overlay-cfgfile', default=None,
                          help='configuration file specifying plot settings '
                          'for image overlays. (default: %(default)s)')
    plotargs.add_argument('--overwrite', action='store_true',
                          help='overwrite existing files')
    plotargs.add_argument('--pad-inches', type=float, default=0.1,
                          help="amount of padding around the figure when "
                          "``--bbox-inches`` is 'tight' "
                          '(default: %(default)s)')
    plotargs.add_argument('--plotformat', default=None,
                          choices=('pdf', 'png', 'jpg', 'ps', 'eps', 'svg'),
                          help='plot output format (default: %(default)s)')
    plotargs.add_argument('--plotcfg', default=None,
                          help='configuration file defining plot settings '
                          '(default: %(default)s)')
    plotargs.add_argument('--plotcfgfile', default=None,
                          help='configuration file defining plot settings '
                          '(default: %(default)s)')
    plotargs.add_argument('--plotlabel', default=None,
                          help='override plot legend label string '
                          '(default: %(default)s).')
    plotargs.add_argument('--profile', default='kgraph',
                          choices=('ipynb-inline', 'kgraph', 'paper',
                                   'poster', 'print', 'tiny'),
                          help='set the plot output profile for preconfigured '
                          'output settings (default: %(default)s)')
    plotargs.add_argument('--save-plot-data', action='store_true',
                          help='save plot data to text file')
    plotargs.add_argument('--save-transparent', action='store_true',
                          help='save figure with transparent background')
    plotargs.add_argument('--text', default=None,
                          help='markup plot with this text string '
                          '(default: %(default)s)')
    plotargs.add_argument('--usetex', action='store_true',
                          help='enable tex labels')
    plotargs.add_argument('--verbose', action='store_true',
                          help='turn on verbose output')
    plotargs.add_argument('--with-errorbars', action='store_true',
                          help='plot data with errorbars')
    plotargs.add_argument('--with-inset-errorbars', action='store_true',
                          help='plot inset data with errorbars')

    plotargs.add_argument('--xvar', default=None,
                          help='x variable (default: %(default)s)')
    plotargs.add_argument('--xvar-units', default=None,
                          help='x variable units (default: %(default)s)')
    plotargs.add_argument('--xlabel', default=None,
                          help='xlabel string (default: %(default)s)')
    plotargs.add_argument('--yvar', default=None,
                          help='y variable (default: %(default)s)')
    plotargs.add_argument('--yvar-units', default=None,
                          help='y variable units (default: %(default)s)')
    plotargs.add_argument('--ylabel', default=None,
                          help='ylabel string (default: %(default)s)')

    plotargs.add_argument('--xmin', metavar='X_MIN', type=float,
                          default=None, help='x-axis min limit '
                          'Deprecated. Use `--left-limit`. '
                          '(default: %(default)s)')
    plotargs.add_argument('--left-limit', metavar='LEFT_XLIMIT', type=float,
                          default=None, help='x-axis left limit '
                          '(default: %(default)s)')
    plotargs.add_argument('--left-limit-scale-factor', type=float,
                          default=0.9, help='``--left-limit`` '
                          'scale-factor (default: %(default)s)')
    plotargs.add_argument('--scale-left-limit', action='store_true',
                          help='scale left limit by '
                          '`--left-limit-scale-factor`')

    plotargs.add_argument('--xmax', metavar='X_MAX', type=float,
                          default=None, help='x-axis max limit '
                          'Deprecated. Use `--right-limit`. '
                          '(default: %(default)s)')
    plotargs.add_argument('--right-limit', metavar='RIGHT_XLIMIT', type=float,
                          default=None, help='x-axis right limit '
                          '(default: %(default)s)')
    plotargs.add_argument('--right-limit-scale-factor', type=float,
                          default=1.1, help='``--right-limit`` '
                          'scale-factor (default: %(default)s)')
    plotargs.add_argument('--scale-right-limit', action='store_true',
                          help='scale right limit by '
                          '`--right-limit-scale-factor`')

    plotargs.add_argument('--ymin', metavar='Y_MIN', type=float,
                          default=None, help='y-axis min limit. '
                          'Deprecated. Use `--bottom-limit`. '
                          '(default: %(default)s)')
    plotargs.add_argument('--bottom-limit', metavar='BOTTOM_YLIMIT',
                          type=float, default=None, help='y-axis bottom limit '
                          '(default: %(default)s)')
    plotargs.add_argument('--bottom-limit-scale-factor', type=float,
                          default=0.9, help='``--bottom-limit`` '
                          'scale-factor (default: %(default)s)')
    plotargs.add_argument('--scale-bottom-limit', action='store_true',
                          help='scale bottom limit by '
                          '`--bottom-limit-scale-factor`')

    plotargs.add_argument('--ymax', metavar='Y_MAX', type=float,
                          default=None, help='y-axis max limit '
                          'Deprecated. Use `--top-limit`. '
                          '(default: %(default)s)')
    plotargs.add_argument('--top-limit', metavar='TOP_YLIMIT', type=float,
                          default=None, help='y-axis top limit '
                          '(default: %(default)s)')
    plotargs.add_argument('--top-limit-scale-factor', type=float,
                          default=1.1, help='``--top-limit`` '
                          'scale-factor (default: %(default)s)')
    plotargs.add_argument('--scale-top-limit', action='store_true',
                          help='scale top limit by '
                          '`--top-limit-scale-factor`')

    plotargs.add_argument('--walk-dirs', default=None,
                          nargs=argparse.REMAINDER,
                          help='walk directories to search for plot file')

    return parser


def cmap_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add-fig-ref', action='store_true',
                        help='add figure reference to top left corner')
    parser.add_argument('--alpha', type=float, default=0.9,
                        help='alpha blending (transparency) value '
                        '(default: %(default)s)')
    parser.add_argument('--aspectratio', type=float, default=None,
                        help='aspect ratio of figure (default: %(default)s)')
    parser.add_argument('--bbox-inches', default='tight',
                        help="Bbox in inches. Only the given portion of the "
                        "figure is saved. If 'tight', try to figure out the "
                        "tight bbox of the figure (default: %(default)s).")
    parser.add_argument('--cmap', default='jet',
                        choices=('autumn', 'bone', 'cool', 'copper', 'flag',
                                 'gray', 'hot', 'hsv', 'jet', 'pink', 'prism',
                                 'spectral', 'spring', 'summer', 'winter'),
                        help='colormap (default: %(default)s)')
    parser.add_argument('--disable-savefig', action='store_true',
                        help='disable figure saving')
    parser.add_argument('--disable-plotting', action='store_true',
                        help="Perform the data analysis, but don't plot data.")
    parser.add_argument('--file-num', type=int, default=None,
                        help='starting file number (default: %(default)s)')
    parser.add_argument('--fname-prefix', default=None,
                        help='prepend plot file name with this prefix '
                        '(default: %(default)s)')
    parser.add_argument('--fname-suffix', default=None,
                        help='append plot file name with this suffix '
                        '(default: %(default)s)')
    parser.add_argument('--hide-color-bar', action='store_true',
                        help='hide color bar')
    parser.add_argument('--interpolation', default='nearest',
                        choices=('nearest', 'bilinear', 'bicubic', 'spline16',
                                 'spline36', 'hanning', 'hamming', 'hermite',
                                 'kaiser', 'quadric', 'catrom', 'gaussian',
                                 'bessel', 'mitchell', 'sinc', 'lanczos'),
                        help='interpolation algorithm for image plot '
                        '(default: %(default)s)')
    parser.add_argument('--ncols', type=int, default=None,
                        help='number of plot cols (default: %(default)s)')
    parser.add_argument('--nrows', type=int, default=None,
                        help='number of plot rows (default: %(default)s)')
    parser.add_argument('--outpath', default=os.getcwd(),
                        help='output path (default: %(default)s)')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    parser.add_argument('--pad-inches', type=float, default=0.1,
                        help="amount of padding around the figure when "
                        "``--bbox-inches`` is 'tight' (default: %(default)s)")
    parser.add_argument('--plotformat', default=None,
                        choices=('pdf', 'png', 'jpg', 'ps', 'eps', 'svg'),
                        help='plot output format (default: %(default)s)')
    parser.add_argument('--plotcfgfile', default=None,
                        help='configuration file defining plot settings '
                        '(default: %(default)s)')
    parser.add_argument('--profile', default='kgraph',
                        choices=('ipynb-inline', 'kgraph', 'paper',
                                 'poster', 'print', 'tiny'),
                        help='set the plot output profile for preconfigured '
                        'output settings (default: %(default)s)')
    parser.add_argument('--save-plot-data', action='store_true',
                        help='save plot data to text file')
    parser.add_argument('--save-transparent', action='store_true',
                        help='save figure with transparent background')
    parser.add_argument('--usetex', action='store_true',
                        help='enable tex labels')
    parser.add_argument('--verbose', action='store_true',
                        help='turn on verbose output')

    return parser
