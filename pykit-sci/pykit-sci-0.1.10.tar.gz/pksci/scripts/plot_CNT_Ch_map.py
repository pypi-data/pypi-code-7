# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
==========================================================================
Script to plot nanotube properties (:mod:`pksci.scripts.plot_CNT_Ch_map`)
==========================================================================

.. currentmodule:: pksci.scripts.plot_CNT_Ch_map

Examples
--------
::

    > plot_CNT_Ch_map --usetex --outpath plots

"""
from __future__ import absolute_import, division, print_function

from collections import OrderedDict

#import os
#import re
import sys

from pkg_resources import resource_filename

from configobj import ConfigObj
from validate import Validator

try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as pe
    from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter, \
        FixedLocator
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
except ImportError:
    print('you need to install matplotlib')
    sys.exit(1)

import numpy as np

from sknano.structures import Nanotube, generate_Ch_list, \
    generate_Ch_property_grid

from ..tools import get_fpath
#from pksci.tools import rounddown2nearestN, roundup2nearestN
from ..tools.mpltools import color_dict, get_mpl_rcParams, \
    plotstr, texstr, cmap_argparser

var_texstr = \
    {u'd': 'd = gcd(n, m)',
     u'd_R': texstr(r'\mathsf{d_R = gcd(2m+n, 2n+m)}'),
     u'Ch': texstr(r'\mathsf{C_{h}}') + ' (' + unicode(u'\u00c5') + ')',
     u'Ch_per_a': texstr(r'\mathsf{C_{h}/a}'),
     u'd_t': texstr(r'\mathsf{d_t}') + ' (' + unicode(u'\u00c5') + ')',
     u'T': texstr(r'\mathsf{T}') + ' (' + unicode(u'\u00c5') + ')',
     u'T_per_a': texstr(r'\mathsf{T/a}'),
     u'Natoms': texstr(r'\mathsf{N_{atoms/cell}}'),
     u'Natoms_per_nm': texstr(r'\mathsf{N_{atoms/cell}/nm}'),
     u'mass': texstr(r'\mathsf{m_{tube}}'),
     u'linear_mass_density': texstr(r'\mathsf{m_{tube}/nm}'),
     u'bundle_density': unicode(u'\u03c1') + texstr(r'\mathsf{_{bundle}}')
     + '(n, m) (g/cm' + r"$\mathsf{^{3}}$" + ')',
     u'bundle_density (d_vdw=0)': unicode(u'\u03c1')
     + texstr(r'\mathsf{_{bundle}} (n, m)') + r'/(d$\mathsf{_{vdw}}$=0)',
     u'mwcnt-Ch': texstr(r'\mathsf{C_{h}}^{\mathsf{MWCNT}}'),
     u'mwcnt-d_t': texstr(r'\mathsf{d_{t}}^{\mathsf{MWCNT}}')}

var_txtstr = \
    {u'd': 'd = gcd(n, m)',
     u'd_R': texstr(r'\mathsf{d_R = gcd(2m+n, 2n+m)}'),
     u'Ch': texstr(r'\mathsf{C_{h}}') + ' (' + unicode(u'\u00c5') + ')',
     u'Ch_per_a': texstr(r'\mathsf{C_{h}/a}'),
     u'd_t': texstr(r'\mathsf{d_t}') + ' (' + unicode(u'\u00c5') + ')',
     u'T': texstr(r'\mathsf{T}') + ' (' + unicode(u'\u00c5') + ')',
     u'T_per_a': texstr(r'\mathsf{T/a}'),
     u'Natoms': texstr(r'\mathsf{N_{atoms/cell}}'),
     u'Natoms_per_nm': texstr(r'\mathsf{N_{atoms/cell}/nm}'),
     u'mass': texstr(r'\mathsf{m_{tube}}'),
     u'linear_mass_density': texstr(r'\mathsf{m_{tube}/nm}'),
     u'bundle_density': unicode(u'\u03c1') + texstr(r'\mathsf{_{bundle}}')
     + '(n, m) (g/cm' + r"$\mathsf{^{3}}$" + ')',
     u'bundle_density (d_vdw=0)': unicode(u'\u03c1')
     + texstr(r'\mathsf{_{bundle}} (n, m)') + r'/(d$\mathsf{_{vdw}}$=0)',
     u'mwcnt-Ch': texstr(r'\mathsf{C_{h}}^{\mathsf{MWCNT}}'),
     u'mwcnt-d_t': texstr(r'\mathsf{d_{t}}^{\mathsf{MWCNT}}')}


def plot_CNT_Ch_map(args):

    majorFormatterStr = plotstr('%d', usetex=args.usetex, roman=False)
    formatterDict = {}
    #unitsDict = {}
    dStrFormatList = [u'd', u'd_R', u'N', u'Natoms', u'Natoms_per_nm']
    formatterDict.update(
        dict.fromkeys(
            dStrFormatList,
            FormatStrFormatter(
                plotstr('%d', usetex=args.usetex, roman=True))))

    fStrFormatList = [u'Ch', u'Ch_per_a', u'd_t', u'T', u'T_per_a',
                      u'mwcnt-Ch', u'mwcnt-d_t']
    formatterDict.update(
        dict.fromkeys(
            fStrFormatList,
            FormatStrFormatter(
                plotstr('%3.1f', usetex=args.usetex, roman=True))))

    fStrFormatList2 = [u'bundle_density', u'bundle_density (d_vdw=0)']
    formatterDict.update(
        dict.fromkeys(
            fStrFormatList2,
            FormatStrFormatter(
                plotstr('%3.2f', usetex=args.usetex, roman=True))))

    eStrFormatList = [u'mass', u'linear_mass_density']

    formatterDict.update(
        dict.fromkeys(
            eStrFormatList,
            FormatStrFormatter(
                plotstr('%2.1e', usetex=args.usetex, roman=True))))

    xlabelStr = plotstr('n', usetex=args.usetex, roman=True)
    ylabelStr = plotstr('m', usetex=args.usetex, roman=True)

    figkwargs = \
        get_mpl_rcParams(mpl, profile=args.profile,
                         usetex=args.usetex,
                         aspectratio=args.aspectratio)

    cmap = mpl.cm.get_cmap(args.cmap)

    fig, ax = plt.subplots(1, 1)

    compute_property = args.compute_property

    imax = args.max_index

    n = np.arange(0, imax + 1, dtype=int)
    m = np.arange(0, imax + 1, dtype=int)

    grid = generate_Ch_property_grid(compute=compute_property,
                                     imax=imax)

    vmin = grid[(grid > -1)].min()
    vmax = grid.max()
    #print('vmin: {}, vmax: {}'.format(vmin, vmax))
    #scaled_vmin = vmin / 1e-21
    #scaled_vmax = vmax / 1e-21
    #print('scaled_vmin: {}, scaled_vmax: {}'.format(
    #    scaled_vmin, scaled_vmax))
    cnorm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    implt = ax.imshow(grid.T, origin='lower', aspect='auto', cmap=cmap,
                      norm=cnorm, interpolation=args.interpolation)

    implt.cmap.set_bad(color_dict['white'])
    implt.cmap.set_under(color_dict['white'])
    implt.cmap.set_over(color_dict['white'])

    if args.show_colorbar:
        cbar_ticks = np.linspace(vmin, vmax, 10).tolist()

        if args.inset_colorbar:
            axins = \
                inset_axes(ax, width="90%", height="4%", loc=8)

            plt.colorbar(implt, cax=axins, ticks=cbar_ticks,
                         format=formatterDict[compute_property],
                         orientation='horizontal')

            axins.xaxis.set_ticks_position("top")
            cbar_fontsize = figkwargs['cbar.label.fontsize']
            cbar_xticklabels = axins.xaxis.get_ticklabels()
            plt.setp(cbar_xticklabels, color='w',
                     fontsize=cbar_fontsize)
            cbar_xticklines = axins.xaxis.get_ticklines()
            plt.setp(cbar_xticklines, color='w')
            axins.tick_params(
                axis='both', which='major',
                length=figkwargs['inset.axes.tick.major.size'],
                width=figkwargs['inset.axes.tick.width'],
                direction='inout')
        else:

            cbar_format_str = '%.1e'
            #cbar_number_units = r'$\mathsf{\frac{g}{nm}}$'
            #cbar_format_str = ' '.join((cbar_number_format,
            #                            cbar_number_units))
            cbar_formatter = \
                FormatStrFormatter(cbar_format_str)

            cax = fig.add_axes([0.125, -0.08, 0.775, 0.03])
            cbar = mpl.colorbar.ColorbarBase(
                cax, cmap=cmap, norm=cnorm, extend='neither',
                ticks=cbar_ticks, format=cbar_formatter,
                orientation='horizontal')

            custom_ticklabels = []
            scale_factor = 1e-21
            for tickindex, tickvalue in \
                    enumerate(cbar_ticks, start=1):

                custom_label = \
                    '{:.1f}'.format(tickvalue / scale_factor)

                #if tickindex == len(cbar_ticks):
                #    custom_label += \
                #        r'$\times{}\mathsf{10^{' + \
                #        '{}{:d}'.format('-', 21) + \
                #        r'}}\mathsf{\frac{g}{nm}}$'
                #    if units is not None:
                #        custom_label = \
                #            ' '.join((custom_label, units))

                custom_ticklabels.append(custom_label)

            #plt.colorbar(implt, extend='neither',
            #             ticks=cbar_ticks,
            #             format=cbar_formatter,
            #             use_gridspec=True,
            #             orientation='vertical')

            cbar.ax.set_xticklabels(custom_ticklabels)
            if args.cbar_labelsize is not None:
                cbar.ax.tick_params(
                    labelsize=args.cbar_labelsize)

            if args.cbar_tick_length is not None:
                cbar.ax.tick_params(
                    length=args.cbar_tick_length)
            #if args.custom_ticklabels:
            #    cbar_ticklabels = cbar.ax.get_yticklabels()

            #    custom_ticklabels = []
            #    for textobj in cbar_ticklabels:
            #        ticklabel = textobj.get_text

    if args.overlay_dt_contours:
        dt_grid = generate_Ch_property_grid(compute='dt', imax=imax)
        dt_levels = np.linspace(5, 30, 6, dtype=int)
        #dt_levels = np.linspace(5, 25, 3, dtype=int)

        cntr_lw = mpl.rcParams['lines.linewidth']
        implt_cntr = \
            ax.contour(dt_grid.T, levels=dt_levels,
                       colors='w', linewidths=cntr_lw,
                       extent=(n[0]-0.5, n[-1]+0.5,
                               m[0]-0.5, m[-1]+0.5),
                       extend='both', antialiased=True,
                       alpha=0.75)

        if args.label_dt_contours:

            cntr_number_units = \
                r'$\mathsf{\AA}$' if args.usetex else u'\u212b'
            cntr_number_format = '%d'
            cntr_label_format_str = \
                ' '.join((cntr_number_format,
                          cntr_number_units))

            clabel_fontsize = \
                figkwargs['contour.label.fontsize']

            implt_clabels = \
                ax.clabel(
                    implt_cntr,
                    [5, 15, 25],
                    fmt=FormatStrFormatter(
                        cntr_label_format_str),
                    fontsize=clabel_fontsize,
                    inline=True,
                    inline_spacing=20,
                    use_clabeltext=True)

            label_pe = pe.withStroke(
                linewidth=mpl.rcParams['lines.linewidth'],
                foreground='k')
            plt.setp(implt_clabels, path_effects=[label_pe])

    nticks = np.arange(0, imax + 1, 5, dtype=int)
    mticks = np.arange(0, imax + 1, 5, dtype=int)

    xminorLocator = AutoMinorLocator(n=5)
    yminorLocator = AutoMinorLocator(n=5)
    xmajorLocator = FixedLocator(mticks)
    ymajorLocator = FixedLocator(nticks)

    ax.xaxis.set_minor_locator(xminorLocator)
    ax.yaxis.set_minor_locator(yminorLocator)

    ax.xaxis.set_major_locator(xmajorLocator)
    ax.yaxis.set_major_locator(ymajorLocator)

    majorFormatter = \
        FormatStrFormatter(majorFormatterStr)

    ax.xaxis.set_major_formatter(majorFormatter)
    ax.yaxis.set_major_formatter(majorFormatter)

    if args.highlight_custom_values and args.custom_config is not None:

        cfgspec = \
            resource_filename('pksci',
                              'configfiles/configspecs/plot_CNT_Ch_map.cfg')
        cfgobj = \
            ConfigObj(args.custom_config, configspec=cfgspec, unrepr=True)

        validator = Validator()
        cfgobj.validate(validator)

        print('cfgobj.sections: {}'.format(cfgobj.sections))

        #if compute_property in cfgobj.sections:

        for section in cfgobj.sections:
            if section == compute_property:
                pass
                #label = section.split('-')[-1]

        synthetic_type_plot_dict = OrderedDict()
        synthetic_type_plot_dict['CoMoCAT'] = \
            {'g_per_nm': 1.6905e-21, 'color': 'r',
             'marker': 's', 'markersize': 45}
        synthetic_type_plot_dict['Laser-He'] = \
            {'g_per_nm': 2.2719e-21, 'color': 'b',
             'marker': 'o', 'markersize': 50}
        synthetic_type_plot_dict['Laser-Ar'] = \
            {'g_per_nm': 4.3606e-21, 'color': 'g',
             'marker': '^', 'markersize': 50}

        for synthetic_type, plot_dict in \
                synthetic_type_plot_dict.iteritems():
            g_per_nm = plot_dict['g_per_nm']

            filter_list = \
                [[compute_property, '>=', 0.9 * g_per_nm],
                 [compute_property, '<=', 1.1 * g_per_nm]]

            highlighted_Ch_list = \
                Nanotube.filter_Ch_list(
                    Ch_list=generate_Ch_list(ns=n.tolist(),
                                             ms=m.tolist()),
                    property_filters=filter_list)

            xdata = []
            ydata = []
            for Ch in highlighted_Ch_list:
                xdata.append(Ch[0])
                ydata.append(Ch[1])

            ax.scatter(xdata, ydata,
                       c=plot_dict['color'],
                       marker=plot_dict['marker'],
                       s=plot_dict['markersize'],
                       linewidths=0.25,
                       label=synthetic_type)

        if args.show_legend:
            legend_loc = args.legend_loc
            legend_fontsize = args.legend_fontsize
            legend_ncol = args.legend_ncol
            if legend_fontsize is None:
                legend_fontsize = figkwargs['legend.fontsize']

            ax.legend(loc=legend_loc,
                      fontsize=legend_fontsize,
                      ncol=legend_ncol,
                      frameon=True, fancybox=True,
                      framealpha=0.5,
                      scatterpoints=1)

        starred_Ch_plot_dict = OrderedDict()

        #if args.symmetric_highlights:
        #    starred_Ch_plot_dict[(6, 5)] = \
        #        {'dx': -0.5, 'dy': 0.5}
        #    #starred_Ch_plot_dict[(7, 6)] = \
        #    #    {'dx': -0.5, 'dy': 0.5}
        #    starred_Ch_plot_dict[(8, 7)] = \
        #        {'dx': -0.5, 'dy': 0.5}
        #    starred_Ch_plot_dict[(10, 10)] = \
        #        {'dx': 0, 'dy': -0.75}

        starred_Ch_plot_dict[(6, 5)] = \
            {'dx': 1, 'dy': 0}
        #starred_Ch_plot_dict[(7, 6)] = \
        #    {'dx': -1, 'dy': 0}
        starred_Ch_plot_dict[(8, 7)] = \
            {'dx': 1, 'dy': 0}
        starred_Ch_plot_dict[(10, 10)] = \
            {'dx': 0, 'dy': -0.75}

        for Ch, xy_offset in starred_Ch_plot_dict.iteritems():
            starred_color = 'y'
            ax.scatter(Ch[0], Ch[1], s=80,
                       c=starred_color,
                       linewidths=0.25,
                       marker='*')
            #if args.symmetric_highlights and Ch[0] != Ch[1]:
            #    ax.scatter(Ch[1], Ch[0], s=80,
            #               c=starred_color,
            #               linewidths=0.25,
            #               marker='*')

            xoffset = xy_offset['dx']
            yoffset = xy_offset['dy']
            xypos = (Ch[0] + xoffset, Ch[1] + yoffset)
            annotation_text_pe = pe.withStroke(
                linewidth=mpl.rcParams['lines.linewidth'] / 2,
                foreground='k')
            annotation_fontsize = \
                figkwargs['text.fontsize'] + 2
            ax.annotate(str(Ch), xy=xypos, xytext=(0, 0),
                        xycoords='data',
                        textcoords='offset points',
                        arrowprops=None,
                        ha='center', va='center',
                        fontsize=annotation_fontsize,
                        fontweight='bold', color='w',
                        path_effects=[annotation_text_pe])

        ax.set_xlim(0, n.max())
        ax.set_ylim(0, m.max())

    if args.add_text_label:
        label_bg_patch = \
            mpl.patches.FancyBboxPatch(
                (0.025, 0.9), width=0.3, height=0.1,
                boxstyle='round,pad=0.2',
                facecolor='k', edgecolor='none',
                aa=True, transform=ax.transAxes,
                alpha=0.7, mutation_scale=0.05)
        ax.add_patch(label_bg_patch)

        label_str = \
            var_texstr[compute_property] if args.usetex else \
            var_txtstr[compute_property]

        label_fontsize = figkwargs['text.label.fontsize']
        text_label = \
            ax.text(0.05, 0.915,
                    label_str, transform=ax.transAxes,
                    fontsize=label_fontsize,
                    ha='left', va='baseline', color='w')
        label_bg_patch.set_zorder(
            text_label.get_zorder() - 0.5)

    if args.add_fig_ref:
        ref_bg_patch = \
            mpl.patches.FancyBboxPatch(
                (0.025, 0.9),
                width=0.08,
                height=0.08,
                boxstyle='round,pad=0.2',
                facecolor='k',
                edgecolor='none',
                aa=True,
                transform=ax.transAxes,
                alpha=0.7,
                mutation_scale=0.05)
        ax.add_patch(ref_bg_patch)

        fig_ref_fontsize = \
            figkwargs['text.label.fontsize'] + 3
        fig_ref = \
            ax.text(0.065, 0.915, args.ref_string,
                    fontsize=fig_ref_fontsize,
                    transform=ax.transAxes,
                    ha='center', va='baseline',
                    color='w')
        ref_bg_patch.set_zorder(fig_ref.get_zorder()-0.5)

    ax.set_xlabel(xlabelStr, labelpad=figkwargs['labelpad'])
    ax.set_ylabel(ylabelStr, labelpad=figkwargs['labelpad'])

    ax.tick_params(axis='both', which='minor',
                   length=figkwargs['tick.minor.size']-1)
    ax.tick_params(axis='both', which='major',
                   length=figkwargs['tick.major.size']-2)

    fname = compute_property + '_plot'
    fout = get_fpath(fname=fname, ext=args.plotformat,
                     outpath=args.outpath,
                     overwrite=args.overwrite, add_fnum=True,
                     fnum=args.file_num, verbose=True)

    fig.set_size_inches(figkwargs['xdim'], figkwargs['ydim'])
    fig.savefig(fout, transparent=args.save_transparent,
                bbox_inches=args.bbox_inches,
                pad_inches=args.pad_inches)

    del fig, ax


def argparser():
    parser = cmap_argparser()
    parser.add_argument('--ref-string', default=None,
                        help='reference string to overlay '
                        '(default: %(default)s)')
    parser.add_argument('--add-text-label', action='store_true',
                        help='add text label')
    parser.add_argument('--cbar-labelsize', type=int, default=None,
                        help='colorbar label fontsize (default: %(default)s)')
    parser.add_argument('--cbar-tick-length', type=float, default=None,
                        help='colorbar tick length (default: %(default)s)')
    parser.add_argument('--show-colorbar', action='store_true',
                        help='show colorbar')
    parser.add_argument('--inset-colorbar', action='store_true',
                        help='use inset colorbar')
    parser.add_argument('--show-legend', action='store_true',
                        help='show plot legend for custom plot values')
    parser.add_argument('--legend-loc', default='best',
                        help='legend location (default: %(default)s)')
    parser.add_argument('--legend-fontsize', default=None,
                        help='legend fontsize (default: %(default)s)')
    parser.add_argument('--legend-ncol', default=1,
                        help='number of legend colums (default: %(default)s)')
    parser.add_argument('--highlight-custom-values', action='store_true',
                        help='plot custom values')
    parser.add_argument('--custom-config', default=None,
                        help='config file with custom highlight settings')
    parser.add_argument('--custom-ticklabels', action='store_true',
                        help='use custom tick labels')
    #parser.add_argument('--symmetric-highlights', action='store_true',
    #                    help='plot symmetric highlighted values')
    parser.add_argument('--overlay-dt-contours', action='store_true',
                        help='overlay diameter contour lines')
    parser.add_argument('--label-dt-contours', action='store_true',
                        help='label diameter contour lines')
    parser.add_argument('--compute-property', default=None,
                        help='CNT property to plot')
    parser.add_argument('--max-index', type=int, default=10,
                        help='maximum chiral index')
    return parser


def main():

    args = argparser().parse_args()
    plot_CNT_Ch_map(args)

if __name__ == '__main__':
    sys.exit(main())
