# -*- coding: utf-8 -*-
"""
===============================================================================
Parsers for plot config files (:mod:`pksci.tools.mpltools._plotcfgparser`)
===============================================================================

.. currentmodule:: pksci.tools.mpltools._plotcfgparser

"""
from __future__ import division, print_function, absolute_import

__docformat__ = 'restructuredtext'

import argparse
import os
import sys
from collections import deque, OrderedDict
from pkg_resources import resource_filename

from configobj import ConfigObj, get_extra_values
import numpy as np

try:
    from validate import Validator
except ImportError as e:
    print(e)
    print('You need to install the ``validate`` module. Run\n'
          '``pip install validate`` if you have admin privileges or else\n'
          '``pip install --user validate``')
    sys.exit(1)

from ..datautils import DataSet, load_data, load_fixed_width_data
from .._strfuncs import split_replace
from ._luts import color_dict
from ._strings import generate_axis_label_dict, plotstr

__all__ = ['PlotConfig', 'PlotConfigParserError', 'PlotConfigParser',
           'XYPlotConfigParser']


class PlotConfig(object):
    """Dummy class to hold plot config settings."""
    pass


class PlotConfigParserError(Exception):
    """Base class for any :class:`PlotConfigParser` errors."""
    pass


class PlotConfigParser(object):
    """Base class for parsing plot config files.

    Parameters
    ----------
    argparser : :class:`~python:argparse.ArgumentParser`, optional
    plotcfgfile : str
    insetcfgfile : str
    overlaycfgfile : str
    cfgspec : {None, str}, optional
    validate : bool, optional

    """
    def __init__(self, argparser=None, plotcfgfile=None, insetcfgfile=None,
                 overlaycfgfile=None, cfgspec=None, validate=True):

        self._args = None
        self._argdict = {}

        if argparser is not None and \
                isinstance(argparser, argparse.ArgumentParser):
            self._args = argparser.parse_args()
            self._argdict = vars(self._args)

        self._dirs = None
        if self._args.walk_dirs is not None:
            self._dirs = deque(self._args.walk_dirs)

        self._plotcfgfile = plotcfgfile
        if (plotcfgfile is None and self._args is not None and
                self._args.plotcfgfile is None and
                self._args.plotcfg is None) or \
                (plotcfgfile is None and argparser is None):
            raise PlotConfigParserError('specify plotcfgfile or argparser '
                                        'with plotcfgfile argument')
        elif plotcfgfile is None and self._args is not None:
            if self._args.plotcfgfile is not None:
                self._plotcfgfile = self._args.plotcfgfile
            elif self._args.plotcfg is not None:
                self._plotcfgfile = self._args.plotcfg

        self._cfgspec = cfgspec
        self._configobj = \
            ConfigObj(self._plotcfgfile, configspec=self._cfgspec, unrepr=True)

        if validate:
            self._validate()

        self._datasets = OrderedDict()
        self._parse_datasets()

        self._plotconfig = PlotConfig()
        self._parse_plotcfg()

        self._flattened_datasets = OrderedDict()
        self._flatten_datasets()
        self._parse_xydata()

        if self._args is not None:
            self._check_argparser_overrides()

    @property
    def config(self):
        return self._plotconfig

    @property
    def configobj(self):
        return self._configobj

    @property
    def parsed_args(self):
        return self._args

    @property
    def datasets(self):
        return self._flattened_datasets

    def _check_argparser_overrides(self):
        if self._args.disable_legend:
            self._plotconfig.disable_legend = True
        if self._args.legend_frameon:
            self._plotconfig.legend_frameon = True

        if self._args.file_num is not None:
            self._plotconfig.output.file_num = self._args.file_num
        if self._args.fname_prefix is not None:
            self._plotconfig.output.fname_prefix = self._args.fname_prefix
        if self._args.fname_suffix is not None:
            self._plotconfig.output.fname_suffix = self._args.fname_suffix

        if self._args.overwrite:
            self._plotconfig.output.overwrite = True
        if self._args.plotformat is not None:
            self._plotconfig.output.plotformat = self._args.plotformat
        if self._args.save_transparent:
            self._plotconfig.output.save_transparent = True

        if self._args.xlabel is not None:
            self._plotconfig.xaxis.label = self._args.xlabel
        if self._args.xvar is not None:
            self._plotconfig.xaxis.var = self._args.xvar

        if self._args.ylabel is not None:
            self._plotconfig.yaxis.label = self._args.ylabel
        if self._args.yvar is not None:
            self._plotconfig.yaxis.var = self._args.yvar

    def _parse_datasets(self):
        for dataset_id in self._configobj['datasets'].sections:
            dataset_config = self._configobj['datasets'][dataset_id]
            if len(dataset_config.sections) == 0:
                self._datasets.depth = 1
                ds = DataSet()

                if dataset_config['axhline']:
                    ds.axhline = True
                    ds.ydata = dataset_config['axhline_y']
                    ds.xdata = 0
                elif dataset_config['axvline']:
                    ds.axvline = True
                    ds.xdata = dataset_config['axhline_x']
                    ds.ydata = 0
                else:
                    ds.dataformat = dataset_config['dataformat']
                    ds.fname = dataset_config['fname']
                    ds.path = dataset_config['path']

                self._parse_data(dataset=ds)
                self._datasets[dataset_id] = ds
            else:
                self._datasets[dataset_id] = OrderedDict()
                self._datasets.depth = 2
                for subset_id in dataset_config.sections:
                    subset_config = dataset_config[subset_id]
                    subset_ds = DataSet()

                    if subset_config['axhline']:
                        subset_ds.axhline = True
                        subset_ds.ydata = subset_config['axhline_y']
                        subset_ds.xdata = 0
                    elif subset_config['axvline']:
                        subset_ds.axvline = True
                        subset_ds.ydata = 0
                        subset_ds.xdata = subset_config['axhline_x']
                    else:
                        subset_ds.dataformat = subset_config['dataformat']
                        if subset_ds.dataformat is None and \
                                dataset_config['dataformat'] is not None:
                            subset_ds.dataformat = dataset_config['dataformat']

                        subset_ds.fname = subset_config['fname']
                        if subset_ds.fname is None and \
                                dataset_config['fname'] is not None:
                            subset_ds.fname = dataset_config['fname']

                        subset_ds.path = subset_config['path']
                        if subset_ds.path is None and \
                                dataset_config['path'] is not None:
                            subset_ds.path = dataset_config['path']

                    self._parse_data(dataset=subset_ds)
                    self._datasets[dataset_id][subset_id] = subset_ds

    def _parse_data(self, dataset=None):
        if dataset is not None:
            fpath = None
            if dataset.fname is not None and self._dirs is not None:
                fpath = os.path.join(self._dirs.popleft(), dataset.fname)
            elif dataset.fname is not None and os.path.isfile(dataset.fname):
                fpath = dataset.fname
            elif dataset.path is not None and os.path.isfile(dataset.path):
                fpath = dataset.path
            elif dataset.fname is not None and dataset.path is not None and \
                    os.path.isdir(dataset.path):
                if os.path.isfile(os.path.join(dataset.path, dataset.fname)):
                    fpath = os.path.join(dataset.path, dataset.fname)

            if fpath is not None:
                if dataset.dataformat in ['textlog', 'txtlog']:
                    dataset.headers, dataset.data = \
                        load_fixed_width_data(fpath, comments='--', names=True)
                else:
                    dataset.headers, dataset.data = \
                        load_data(fpath, headerlines=1,
                                  skip_lines_starting_with='#')

    def _parse_plotcfg(self):
        """Parse config file and set attributes of plotconfig object."""

        # parse figure plotconfig
        for option in self._configobj['fig_config'].scalars:
            setattr(self._plotconfig, option,
                    self._configobj['fig_config'][option])

        # parse default plot options
        default_plotconfig = self._configobj['plot_config']
        for option in default_plotconfig.scalars:
            try:
                setattr(self._plotconfig, option,
                        color_dict[default_plotconfig[option]])
            except KeyError:
                setattr(self._plotconfig, option, default_plotconfig[option])

        if self._plotconfig.disable_markers:
            self._plotconfig.markersize = 0

        self._plotconfig.strtype = \
            strtype = 'tex' if self._plotconfig.usetex else 'txt'
        var_strings = {}
        var_units = {}
        for d in (var_strings, var_units):
            d[strtype] = {}

        # parse axis plot options
        for axis in default_plotconfig.sections:
            setattr(self._plotconfig, axis, PlotConfig())
            plotaxis = getattr(self._plotconfig, axis)
            for k, v in default_plotconfig[axis].iteritems():
                setattr(plotaxis, k, v)

            var = plotaxis.var
            if var is not None:
                var_strings[strtype][var] = plotstr(var, strtype=strtype)
                units = plotaxis.units
                if units is not None:
                    var_units[strtype][var] = plotstr(units, strtype=strtype)
            else:
                var_strings[strtype][plotaxis[:1]] = plotaxis[:1]

        # set up axis label dict
        #self._plotconfig.var_strings = var_strings
        #self._plotconfig.var_units = var_units
        if self._plotconfig.xaxis.label is None or \
                self._plotconfig.yaxis.label is None:
            self._plotconfig.axis_labels = \
                generate_axis_label_dict(var_dict=var_strings,
                                         units_dict=var_units)

        xaxis = self._plotconfig.xaxis
        if xaxis.label is None:
            if xaxis.var is not None:
                xaxis.label = \
                    self._plotconfig.axis_labels[strtype][xaxis.var]
            else:
                xaxis.label = 'x'

        yaxis = self._plotconfig.yaxis
        if yaxis.label is None:
            if yaxis.var is not None:
                yaxis.label = \
                    self._plotconfig.axis_labels[strtype][yaxis.var]
            else:
                yaxis.label = 'y'

        self._plotconfig.output = PlotConfig()
        for option in self._configobj['output_config'].scalars:
            setattr(self._plotconfig.output, option,
                    self._configobj['output_config'][option])

        self._plotconfig.input = PlotConfig()
        for option in self._configobj['input_config'].scalars:
            setattr(self._plotconfig.input, option,
                    self._configobj['input_config'][option])

        self._plotconfig.input.headers = PlotConfig()
        for option in self._configobj['input_config']['headers'].scalars:
            setattr(self._plotconfig.input.headers, option,
                    self._configobj['input_config']['headers'][option])

        self._plotconfig.datasets = PlotConfig()
        for option in self._configobj['datasets'].scalars:
            try:
                setattr(self._plotconfig.datasets, option,
                        color_dict[self._configobj['datasets'][option]])
            except KeyError:
                setattr(self._plotconfig.datasets, option,
                        self._configobj['datasets'][option])

        # Parse dataset plotconfig
        for dataset_id, dataset in self._datasets.iteritems():
            setattr(self._plotconfig.datasets, dataset_id, PlotConfig())
            dataset_plotconfig = getattr(self._plotconfig.datasets, dataset_id)
            dataset_config = self._configobj['datasets'][dataset_id]
            if isinstance(dataset, DataSet):
                for k, v in dataset_config.iteritems():
                    if v is not None:
                        try:
                            setattr(dataset_plotconfig, k, color_dict[v])
                        except KeyError:
                            setattr(dataset_plotconfig, k, v)
                    elif k in self._configobj['datasets'].scalars and \
                            self._configobj['datasets'][k] is not None:
                        try:
                            setattr(
                                dataset_plotconfig, k,
                                color_dict[self._configobj['datasets'][k]])
                        except KeyError:
                            setattr(
                                dataset_plotconfig, k,
                                self._configobj['datasets'][k])
                    elif hasattr(self._plotconfig, k):
                        setattr(dataset_plotconfig, k,
                                getattr(self._plotconfig, k))
                    #elif k in default_plotconfig.scalars:
                    #    try:
                    #        setattr(dataset_plotconfig, k,
                    #                color_dict[default_plotconfig[k]])
                    #    except KeyError:
                    #        setattr(dataset_plotconfig, k,
                    #                default_plotconfig[k])
                    else:
                        setattr(dataset_plotconfig, k, None)
            elif isinstance(dataset, OrderedDict):
                for subset_id in dataset_config.sections:
                    setattr(dataset_plotconfig, subset_id, PlotConfig())
                    subset_plotconfig = getattr(dataset_plotconfig, subset_id)
                    subset_config = dataset_config[subset_id]
                    for k, v in subset_config.iteritems():
                        if v is not None:
                            try:
                                setattr(subset_plotconfig, k, color_dict[v])
                            except KeyError:
                                setattr(subset_plotconfig, k, v)
                        elif k in dataset_config.scalars and \
                                dataset_config[k] is not None:
                            try:
                                setattr(subset_plotconfig, k,
                                        color_dict[dataset_config[k]])
                            except KeyError:
                                setattr(subset_plotconfig, k,
                                        dataset_config[k])
                        elif k in self._configobj['datasets'].scalars and \
                                self._configobj['datasets'][k] is not None:
                            try:
                                setattr(
                                    subset_plotconfig, k,
                                    color_dict[self._configobj['datasets'][k]])
                            except KeyError:
                                setattr(subset_plotconfig, k,
                                        self._configobj['datasets'][k])
                        elif hasattr(self._plotconfig, k):
                            setattr(subset_plotconfig, k,
                                    getattr(self._plotconfig, k))
                        #elif k in default_plotconfig.scalars:
                        #    try:
                        #        setattr(subset_plotconfig, k,
                        #                color_dict[default_plotconfig[k]])
                        #    except KeyError:
                        #        setattr(subset_plotconfig, k,
                        #                default_plotconfig[k])
                        else:
                            setattr(subset_plotconfig, k, None)

        #self._plotconfig.inset_plotconfig = PlotConfig()

    def _flatten_datasets(self):
        """Generate flattened dataset dictionary."""
        for dataset_id, dataset in self._datasets.iteritems():
            if isinstance(dataset, DataSet):
                self._update_flattened_datasets(
                    key=dataset_id,
                    value=dataset,
                    attr=getattr(self._plotconfig.datasets, dataset_id))
            elif isinstance(dataset, OrderedDict):
                for subset_id, subset_dataset in dataset.iteritems():
                    self._update_flattened_datasets(
                        key=subset_id,
                        value=subset_dataset,
                        attr=getattr(getattr(self._plotconfig.datasets,
                                             dataset_id), subset_id))

    def _update_flattened_datasets(self, key=None, value=None, attr=None):
        if key is not None:
            numbered_key = key + '0'
            i = 1
            while numbered_key in self._flattened_datasets.keys():
                numbered_key = key + str(i)
                i += 1
            self._flattened_datasets[numbered_key] = value
            setattr(self._plotconfig.datasets, numbered_key, attr)

    def _parse_xydata(self):
        # parse datasets xdata/ydata attributes.
        # This code needs to be updated to handle multiple xdata/ydata
        # per dataset.
        header_xvar = self._plotconfig.input.headers.xvar
        header_yvar = self._plotconfig.input.headers.yvar

        if header_yvar is not None:
            for dataset_id, dataset in self._flattened_datasets.iteritems():
                #dataset_plotconfig = \
                #    getattr(self._plotconfig.datasets, dataset_id)
                if dataset.ydata is None:
                    ydata = None
                    #if dataset_plotconfig.axhline:
                    #    ydata = dataset_plotconfig.axhline_y
                    #elif dataset_plotconfig.axvline:
                    #    pass
                    if dataset.dataformat in ('textlog', 'txtlog'):
                        ydata = dataset.data[split_replace(header_yvar)]
                    else:
                        ydata = \
                            dataset.data[:, dataset.headers.index(header_yvar)]

                    dataset.ydata = ydata

                if dataset.xdata is None:
                    xdata = None
                    #if dataset_plotconfig.axvline:
                    #    xdata = dataset_plotconfig.axvline_x
                    #elif dataset_plotconfig.axhline:
                    #    pass
                    if header_xvar is not None:
                        if dataset.dataformat in ('textlog', 'txtlog'):
                            xdata = dataset.data[split_replace(header_xvar)]
                        else:
                            xdata = \
                                dataset.data[:, dataset.headers.index(
                                    header_xvar)]
                    else:
                        xdata = np.arange(0, len(dataset.ydata))

                    dataset.xdata = xdata
        #else:
        #    for dataset_id, dataset in self._flattened_datasets.iteritems():
        #        dataset_plotconfig = \
        #            getattr(self._plotconfig.datasets, dataset_id)
        #        ydata = None
        #        if dataset_plotconfig.axhline:
        #            ydata = dataset_plotconfig.axhline_y
        #        elif dataset_plotconfig.axvline:
        #            pass

        #        dataset.ydata = ydata

        #        xdata = None
        #        if dataset_plotconfig.axvline:
        #            xdata = dataset_plotconfig.axvline_x
        #        elif dataset_plotconfig.axhline:
        #            pass

        #        dataset.xdata = xdata

    def _validate(self):
        if self._cfgspec is not None:
            validator = Validator()
            validated = self._configobj.validate(validator)
            if not validated:
                raise PlotConfigParserError('plotcfg failed validation')
            extra_values = get_extra_values(self._configobj)
            print('extra_values: {}'.format(extra_values))


class XYPlotConfigParser(PlotConfigParser):
    """Plot config parser for standard 2D X-Y plots.

    Parameters
    ----------
    argparser : :class:`~python:argparse.ArgumentParser`, optional
    plotcfgfile : {None, str}, optional
    insetcfgfile : {None, str}, optional
    overlaycfgfile : {None, str}, optional
    cfgspec : {None, str}, optional
    validate : bool, optional

    """
    def __init__(self, argparser=None, plotcfgfile=None, insetcfgfile=None,
                 overlaycfgfile=None, cfgspec=None, validate=True):

        if cfgspec is None:
            cfgspec = resource_filename(
                'pksci', 'configfiles/configspecs/xyplot.cfg')

        super(XYPlotConfigParser, self).__init__(
            argparser=argparser, plotcfgfile=plotcfgfile,
            insetcfgfile=insetcfgfile, overlaycfgfile=overlaycfgfile,
            cfgspec=cfgspec, validate=validate)

        if self._plotconfig.output.fname is None:
            self._plotconfig.output.fname = self._generate_output_fname()

    def _generate_output_fname(self):
        fname = ''
        if self._plotconfig.yaxis.var is not None:
            fname += self._plotconfig.yaxis.var
            if self._plotconfig.xaxis.var is not None:
                fname += '_vs_' + self._plotconfig.xaxis.var

        if len(fname) == 0:
            fname = 'plot'
        if self._plotconfig.output.fname_prefix is not None:
            fname = self._plotconfig.output.fname_prefix + '_' + fname
        if self._plotconfig.output.fname_suffix is not None:
            fname += self._plotconfig.output.fname_suffix

        return fname
