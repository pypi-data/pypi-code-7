# -*- coding: utf-8 -*-
"""
===========================================================================
Classes for reading log files (:mod:`pksci.tools.datautils._logparser`)
===========================================================================

.. currentmodule:: pksci.tools.datautils._logparser

"""
from __future__ import division, print_function, absolute_import

__docformat__ = 'restructuredtext'

from collections import OrderedDict
import sys

__all__ = ['LogParserError', 'TextLogParserError',
           'LogParser', 'TextLogParser']


class LogParserError(Exception):
    """Exception raised for `LogParser` errors."""
    pass


class TextLogParserError(LogParserError):
    """Exception raised for TextLogParser errors."""
    pass


class LogParser(object):
    """Base class for reading log files.

    Parameters
    ----------
    logname : str
    logfile : str
    logtype : str

    """

    def __init__(self, logname=None, logfile=None, logtype=None):

        self._fields = OrderedDict()
        self._field_names = []
        self._field_widths = []
        self._logname = None
        self._logfile = None

    @property
    def fields(self):
        """:py:class:`<python:collections.OrderedDict>` of ``fields``."""
        return self._fields

    @property
    def field_names(self):
        """list of ``field_names``."""
        return self._field_names

    @property
    def field_widths(self):
        """list of ``field_widths``."""
        return self._field_widths

    @property
    def logfile(self):
        """logfile."""
        return self._logfile

    @property
    def logname(self):
        """logname."""
        return self._logname


class TextLogParser(LogParser):
    """
    Class for generating text logs in columnated format.

    Parameters
    ----------
    fields : `<python:collections.OrderedDict>` or `<python:dict>`
        dictionary of (key, value) fields to log
    logname : str
    logfile : str
    mode : str, optional
        file editing mode
    wspad : int, optional

    """

    def __init__(self, fields=None, logname=None, logfile=None,
                 mode='a+', wspad=4):

        self._mode = mode

        if sys.version_info[0] < 3:
            # call super class using python 2 approach
            super(TextLogParser, self).__init__(
                logname=logname, logfile=logfile, logtype='text')
        else:
            # call super class using python 3 approach
            super().__init__(logname=logname, logfile=logfile, logtype='text')

    def read_header(self):
        """Read the header (column) fields."""
        pass

    def read_fields(self):
        """Read fields."""
        pass
