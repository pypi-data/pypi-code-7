# -*- coding: utf-8 -*-
"""
========================================================================
Classes for logging data (:mod:`pksci.tools.datautils._loggenerator`)
========================================================================

.. currentmodule:: pksci.tools.datautils._loggenerator

"""
from __future__ import division, print_function, absolute_import

__docformat__ = 'restructuredtext'

from collections import OrderedDict
from datetime import datetime
import os
import sys

from .._strfuncs import concat_units

__all__ = ['LogGeneratorError', 'TextLogGeneratorError',
           'LogGenerator', 'TextLogGenerator', 'logtype_fext']

logtype_fext = {None: '.log', 'text': '.txt'}


class LogGeneratorError(Exception):
    """Raised when an `import` dependency for any `LogGenerator`
    raises an ImportError"""
    pass


class TextLogGeneratorError(LogGeneratorError):
    """Exception raised for `TextLogGenerator` errors."""
    pass


class LogGenerator(object):
    """Base class for generating log files.

    Parameters
    ----------
    logname : str
    logfile : str
    logtype : str

    """

    def __init__(self, logname=None, logfile=None, logtype=None):

        self.fields = OrderedDict()
        self.field_names = []
        self.field_widths = []

        if logname is None or not isinstance(logname, str):
            logname = 'log'

        logext = logtype_fext[logtype]
        if logfile is None:
            dt = datetime.now()
            timestr = dt.strftime("%Y-%m-%d_%H%M%S")
            logfile = logname + '-' + timestr + logext
        else:
            if not logfile.endswith(logext):
                logfile += logext

        self.logname = logname
        self.logfile = logfile


class TextLogGenerator(LogGenerator):
    """
    Class for generating text logs in columnated format.

    Parameters
    ----------
    fields : :py:class:`~python:collections.OrderedDict` or `dict`
        dictionary of (key, value) fields to log
    logname : str
    logfile : str
    mode : str, optional
        file editing mode
    wspad : int, optional

    """

    def __init__(self, fields=None, logname=None, logfile=None,
                 manual_flush=True, mode='a+', wspad=4):

        self.manual_flush = manual_flush
        self.mode = mode

        if sys.version_info[0] < 3:
            # call super class using python 2 approach
            super(TextLogGenerator, self).__init__(
                logname=logname, logfile=logfile, logtype='text')
        else:
            # call super class using python 3 approach
            super().__init__(logname=logname, logfile=logfile, logtype='text')

        if fields is not None:
            on_field1 = True
            for field_key, field_dict in fields.iteritems():
                field_name = field_dict.get('name')
                field_var = field_dict.get('var')
                field_units = field_dict.get('units')

                if field_name is None:
                    if field_var is not None:
                        if field_units is not None:
                            field_name = concat_units(field_var, field_units)
                        else:
                            field_name = field_var
                    else:
                        field_name = field_key
                else:
                    if field_units is not None:
                        field_name = concat_units(field_name, field_units)

                field_width = field_dict.get('width')
                field_str_template = field_dict.get('field_str_template')

                if field_width is None:
                    if field_str_template is None:
                        field_width = len(field_name)
                    else:
                        field_width = len(field_str_template)
                delim_width = field_width
                if on_field1:
                    on_field1 = False
                else:
                    field_width += wspad

                field_dict = field_dict.copy()
                field_dict.update({'name': field_name})
                field_dict.update(
                    {'delim': delim_width*'-', 'width': field_width})

                self.fields.update({field_key: field_dict})
                self.field_names.append(field_name)
                self.field_widths.append(field_width)

        with open(self.logfile, self.mode) as textlog:
            lines = textlog.readlines()
            if len(lines) == 0:
                self.write_header()

    def __str__(self):
        """String representation of `TextLogGenerator`."""
        return "<TextLogGenerator instance: {}.{}>".format(
            self.logname, self.logfile)

    def dict2logline(self, d):
        logline = ''
        for key, field in self.fields.iteritems():
            if key in d:
                try:
                    logline += \
                        '{0:>{width}.{precision}{ptype}}'.format(d[key],
                                                                 **field)
                except (KeyError, ValueError):
                    try:
                        logline += \
                            '{0:>{width}{ptype}}'.format(d[key], **field)
                    except (KeyError, ValueError):
                        logline += '{0!s:>{width}}'.format(d[key], **field)
            else:
                logline += '{0:>{width}}'.format(None, **field)
        logline += '\n'
        self.write_line(logline)

    def seq2logline(self, seq):
        logline = ''
        for n, field in enumerate(self.fields.itervalues()):
            logline += '{0:>{width}}'.format(seq[n], **field)
        logline += '\n'
        self.write_line(logline)

    def write_header(self, textlog=None):
        """Write the header (column) fields.

        Parameters
        ----------
        log : `TextLogGenerator` instance

        """
        logline = ''
        for field in self.fields.itervalues():
            logline += '{name!s:>{width}}'.format(**field)
        logline += '\n'
        self.write_line(logline, textlog=textlog)

        logline = ''
        for field in self.fields.itervalues():
            logline += '{delim!s:>{width}}'.format(**field)
        logline += '\n'
        self.write_line(logline, textlog=textlog)

    def write_fields(self, fields):
        """Write fields to log.

        Parameters
        ----------
        fields : {dict, sequence}

        """
        if isinstance(fields, dict):
            self.dict2logline(fields)
        elif isinstance(fields, (list, tuple)):
            self.seq2logline(fields)
        else:
            raise TextLogGeneratorError('``fields`` must be dict or sequence.')

    def write_line(self, logline, textlog=None):
        """Write log line.

        Parameters
        ----------
        logline : str
        textlog : `TextLogGenerator` instance

        """
        if textlog is None:
            with open(self.logfile, self.mode) as textlog:
                textlog.write(logline)
                if self.manual_flush:
                    textlog.flush()
                    os.fsync(textlog.fileno())
        elif isinstance(textlog, TextLogGenerator):
            textlog.write_line(logline)
        elif isinstance(textlog, file):
            textlog.write(logline)
            if self.manual_flush:
                textlog.flush()
                os.fsync(textlog.fileno())
        else:
            raise TextLogGeneratorError("Can't write to textlog: {}".format(
                textlog))
