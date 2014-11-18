# -*- coding: utf-8 -*-
"""
===============================================================================
Overlay config parser (:mod:`pksci.tools.mpltools._img_overlay_cfgparser`)
===============================================================================

.. currentmodule:: pksci.tools.mpltools._img_overlay_cfgparser

"""
from __future__ import division, print_function, absolute_import

from pkg_resources import resource_filename

__docformat__ = 'restructuredtext'

from collections import OrderedDict

from configobj import ConfigObj
from validate import Validator

from ..datautils import DataSet

__all__ = ['ImageOverlayConfigParser']


class ImageOverlayConfig(object):
    """Dummy class to hold plot config settings."""
    pass


class ImageOverlayConfigParserError(Exception):
    """Base class for any :py:class:`PlotConfigParser` errors."""
    pass


class ImageOverlayConfigParser(object):
    """Base class for parsing plot config files.

    Parameters
    ----------
    cfgfile : str
    cfgspec : str
    unrepr : bool, optional
    validate : bool, optional

    """
    def __init__(self, cfgfile=None, cfgspec=None, unrepr=True,
                 validate=True, autoparse=True, argparser=None):
        self._cfgfile = cfgfile
        self._cfgspec = cfgspec
        self._img_overlay_config = ImageOverlayConfig()
        if cfgspec is None:
            self._cfgspec = \
                resource_filename(
                    'pksci', 'configfiles/configspecs/img_overlay.cfg')

        self._config = \
            ConfigObj(self._cfgfile, configspec=self._cfgspec, unrepr=unrepr)

        if validate:
            validator = Validator()
            validated = self._config.validate(validator)

        if autoparse:
            self.parse_config()

    @property
    def config(self):
        return self._img_overlay_config
