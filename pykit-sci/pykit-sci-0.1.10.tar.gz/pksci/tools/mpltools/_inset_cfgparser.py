# -*- coding: utf-8 -*-
"""
===============================================================================
Parsers for plot config files (:mod:`pksci.tools.mpltools._plotcfgparser`)
===============================================================================

.. currentmodule:: pksci.tools.mpltools._plotcfgparser

"""
from __future__ import division, print_function, absolute_import

from pkg_resources import resource_filename

__docformat__ = 'restructuredtext'

from collections import OrderedDict

from configobj import ConfigObj
from validate import Validator

from ..datautils import DataSet

__all__ = ['PlotConfig', 'PlotConfigParserError', 'PlotConfigParser']


class PlotConfig(object):
    """Dummy class to hold plot config settings."""
    pass


class PlotConfigParserError(Exception):
    """Base class for any :py:class:`PlotConfigParser` errors."""
    pass


class PlotConfigParser(object):
    """Base class for parsing plot config files.

    Parameters
    ----------
    cfgfile : str
    cfgspec : str
    unrepr : bool, optional
    validate : bool, optional

    """
    def __init__(self, cfgfile=None, cfgspec=None, unrepr=True,
                 validate=True, autoparse=True):
        self._cfgfile = cfgfile
        self._cfgspec = cfgspec
        self._plotconfig = PlotConfig()
        if cfgspec is not None:
            self._cfgspec = \
                resource_filename(
                    'pksci', 'configfiles/configspecs/' + cfgspec)
        else:
            self._cfgspec = \
                resource_filename(
                    'pksci', 'configfiles/configspecs/2dplot.cfg')

        self._config = \
            ConfigObj(self._cfgfile, configspec=self._cfgspec, unrepr=unrepr)

        self._datasets = OrderedDict()

        if validate:
            self.validate()

        if autoparse:
            self.parse_config()
            self.parse_datasets()

    @property
    def config(self):
        return self._plotconfig

    @property
    def configobj(self):
        return self._config

    @property
    def datasets(self):
        return self._datasets

    def parse_config(self):
        """Parse config file and set attributes of plotconfig object."""
        for axis in self._config['default plot settings'].sections:
            setattr(self._plotconfig, axis, PlotConfig())
            for k, v in self._config['default plot settings'][
                    axis].iteritems():
                setattr(getattr(self._plotconfig, axis), k, v)

        for option in self._config['default plot settings'].scalars:
            setattr(self._plotconfig, option,
                    self._config['default plot settings'][option])

        self._plotconfig.figure = PlotConfig()
        for option in self._config['figure settings'].scalars:
            setattr(self._plotconfig.figure, option,
                    self._config['figure settings'][option])

        self._plotconfig.output = PlotConfig()
        for option in self._config['output file options'].scalars:
            setattr(self._plotconfig.output, option,
                    self._config['output file options'][option])

        self._plotconfig.input = PlotConfig()
        for option in self._config['input file properties'].scalars:
            setattr(self._plotconfig.input, option,
                    self._config['input file properties'][option])

        self._plotconfig.datasets = PlotConfig()
        for option in self._config['datasets'].scalars:
            setattr(self._plotconfig.datasets, option,
                    self._config['datasets'][option])

        for dataset in self._config['datasets'].sections:
            setattr(self._plotconfig.datasets, dataset, PlotConfig())
            for k, v in self._config['datasets'][dataset].iteritems():
                setattr(getattr(self._plotconfig.datasets, dataset), k, v)

    def parse_datasets(self):
        for dataset in self._config['datasets'].sections:
            ds = DataSet()
            ds.fname = self._config['datasets'][dataset]['file']
            ds.path = self._config['datasets'][dataset]['path']
            self._datasets[dataset] = ds

    def validate(self):
        validator = Validator()
        validated = self._config.validate(validator)
        if not validated:
            raise PlotConfigParserError('plot config did not pass validation.')
