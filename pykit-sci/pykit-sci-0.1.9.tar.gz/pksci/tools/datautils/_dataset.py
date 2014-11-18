# -*- coding: utf-8 -*-
"""
===============================================================================
Classes for parsing data sets (:mod:`pksci.tools.datautils._dataset`)
===============================================================================

.. currentmodule:: pksci.tools.datautils._dataset

"""
from __future__ import division, print_function, absolute_import

__docformat__ = 'restructuredtext'

__all__ = ['DataSet', 'DataGroup']


class DataSet(object):
    """Class for containing data."""

    def __init__(self):
        self._axhline = self._axvline = None
        self._dataformat = None
        self._fname = None
        self._path = None
        self._fields = None
        self._headers = None
        self._data = None
        self._xdata = None
        self._ydata = None

    @property
    def axhline(self):
        return self._axhline

    @axhline.setter
    def axhline(self, value):
        self._axhline = value

    @property
    def axvline(self):
        return self._axvline

    @axvline.setter
    def axvline(self, value):
        self._axvline = value

    @property
    def dataformat(self):
        return self._dataformat

    @dataformat.setter
    def dataformat(self, value):
        self._dataformat = value

    @dataformat.deleter
    def dataformat(self):
        del self._dataformat

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, value):
        self._fname = value

    @fname.deleter
    def fname(self):
        del self._fname

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @path.deleter
    def path(self):
        del self._path

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    @headers.deleter
    def headers(self):
        del self._headers

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @data.deleter
    def data(self):
        del self._data

    @property
    def xdata(self):
        return self._xdata

    @xdata.setter
    def xdata(self, value):
        self._xdata = value

    @xdata.deleter
    def xdata(self):
        del self._xdata

    @property
    def ydata(self):
        return self._ydata

    @ydata.setter
    def ydata(self, value):
        self._ydata = value

    @ydata.deleter
    def ydata(self, value):
        del self._ydata


class DataGroup(DataSet):
    """Class for containing multiple DataSets"""

    def __init__(self):
        self._groupid = None

    @property
    def groupid(self):
        return self._groupid

    @groupid.setter
    def groupid(self, value):
        self._groupid = value

    @groupid.deleter
    def groupid(self):
        del self._groupid
