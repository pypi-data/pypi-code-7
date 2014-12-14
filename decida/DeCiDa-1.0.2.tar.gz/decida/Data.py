################################################################################
# CLASS    : Data
# PURPOSE  : decida Data object
# AUTHOR   : Richard Booth
# DATE     : Sat Nov  9 11:19:20 2013
# -----------------------------------------------------------------------------
# NOTES    : 
#
# LICENSE  : (BSD-new)
# 
# This software is provided subject to the following terms and conditions,
# which you should read carefully before using the software.  Using this
# software indicates your acceptance of these terms and conditions.  If you
# do not agree with these terms and conditions, do not use the software.
# 
# Copyright (c) 2013 Richard Booth. All rights reserved.
# 
# Redistribution and use in source or binary forms, with or without
# modifications, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following Disclaimer
#       in each human readable file as well as in the documentation and/or
#       other materials provided with the distribution.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following Disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Richard Booth nor the names of contributors
#       (those who make changes to the software, documentation or other
#       materials) may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# 
# Disclaimer
# 
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, INFRINGEMENT AND THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# ANY USE, MODIFICATION OR DISTRIBUTION OF THIS SOFTWARE IS SOLELY AT THE
# USERS OWN RISK.  IN NO EVENT SHALL RICHARD BOOTH OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, INCLUDING,
# BUT NOT LIMITED TO, CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# IN NO EVENT SHALL THE AUTHORS OR DISTRIBUTORS BE LIABLE TO ANY PARTY
# FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES
# ARISING OUT OF THE USE OF THIS SOFTWARE, ITS DOCUMENTATION, OR ANY
# DERIVATIVES THEREOF, EVEN IF THE AUTHORS HAVE BEEN ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# 
# THE AUTHORS AND DISTRIBUTORS SPECIFICALLY DISCLAIM ANY WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.  THIS SOFTWARE
# IS PROVIDED ON AN "AS IS" BASIS, AND THE AUTHORS AND DISTRIBUTORS HAVE
# NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
# MODIFICATIONS.
###############################################################################
import user
import decida
from decida.ItclObjectx    import ItclObjectx
from decida.TextWindow     import TextWindow
from decida.EquationParser import EquationParser
import numpy
##-- cython syntax:
#cimport numpy
#DTYPE = numpy.float64
#ctypedef numpy.float64_t DTYPE_t
##--
import math
import string
import sys
import re
import os
import os.path
import time
from Tkinter import *
from types   import *
import tkSimpleDialog
import tkMessageBox
import tkFileDialog
import tkColorChooser
try :
    import matplotlib.pylab as plt
    _have_mat = True
except :
    _have_mat = False

class Data(ItclObjectx) :
    """ read, write, manipulate data.

    **synopsis**:

    Data manages a 2-dimensional data structure.  Each data column has an
    associated name which can be used to index the data column.
    It has methods for reading and writing various formats of data files,
    appending, sorting, filtering or deleting columns.  It has methods for
    performing column-wise operations, finding level crossings, edges, and
    jitter of transient "signals" (time and signal columns), and
    low-pass filter parameters of ac "signals" (frequency and complex signal
    columns).  And there are many other methods for managing data.

    Data uses the numpy array as the basic 2-dimensional numerical structure.
    Numpy is used to perform column-wise operations and so are performed
    very quickly.

    **constructor arguments**:

        .. option:: \*\*kwargs (dict)

            keyword=value specifications:
            configuration-options

    **configuration options**:

        .. option:: verbose (bool, default=False)

            if True, print out messages

        .. option:: title (str, default="")

            specify data set title
        
    **example**:

        >>> from decida.Data import Data
        >>> d = Data(title="prelayout_data", verbose=True)
        >>> d["verbose"] = False

    **public methods**:

        * public methods from *ItclObjectx*

    """
    _UnaryOp = {
        "-"            : numpy.negative,
        "sign"         : numpy.sign,
        "reciprocal"   : numpy.reciprocal,
        "sqrt"         : numpy.sqrt,
        "square"       : numpy.square,
        "abs"          : numpy.absolute,
        "sin"          : numpy.sin,
        "cos"          : numpy.cos,
        "tan"          : numpy.tan,
        "asin"         : numpy.arcsin,
        "acos"         : numpy.arccos,
        "atan"         : numpy.arctan,
        "exp"          : numpy.exp,
        "expm1"        : numpy.expm1,
        "exp2"         : numpy.exp2,
        "log"          : numpy.log,
        "log10"        : numpy.log10,
        "log2"         : numpy.log2,
        "log1p"        : numpy.log1p,
        "sinh"         : numpy.sinh,
        "cosh"         : numpy.cosh,
        "tanh"         : numpy.tanh,
        "asinh"        : numpy.arcsinh,
        "acosh"        : numpy.arccosh,
        "atanh"        : numpy.arctanh,
        "degrees"      : numpy.degrees,
        "radians"      : numpy.radians,
        "deg2rad"      : numpy.deg2rad,
        "rad2deg"      : numpy.rad2deg,
        "rint"         : numpy.rint,
        "fix"          : numpy.fix,
        "floor"        : numpy.floor,
        "ceil"         : numpy.ceil,
        "trunc"        : numpy.trunc,
    }
    _BinaryOp = {
        "+"            : numpy.add,
        "-"            : numpy.subtract,
        "*"            : numpy.multiply,
        "/"            : numpy.divide,
        "^"            : numpy.power,
        "true_divide"  : numpy.true_divide,
        "floor_divide" : numpy.floor_divide,
        "fmod"         : numpy.fmod,
        "mod"          : numpy.mod,
        "rem"          : numpy.remainder,
        "hypot"        : numpy.hypot,
        "max"          : numpy.maximum,
        "min"          : numpy.minimum,
    }
    _UnaryOpD = {
        "del"          : "_col_del",
        "not"          : "_col_not",
        "!"            : "_col_not",
    }
    _BinaryOpD = {
        "atan2"        : "_col_atan2",
        "dY/dX"        : "_col_diff",
        "integ"        : "_col_integ",
        "=="           : "_col_eq",
        "!="           : "_col_ne",
        "<="           : "_col_le",
        ">="           : "_col_ge",
        "<"            : "_col_lt",
        ">"            : "_col_gt",
        "&&"           : "_col_and",
        "||"           : "_col_or",
        "and"          : "_col_and",
        "or"           : "_col_or",
        "xor"          : "_col_xor",
    }
    @staticmethod
    def _col_del(x) :
        z = numpy.diff(x)
        return numpy.append(z, z[-1])
    @staticmethod
    def _col_atan2(y, x) :
        return numpy.unwrap(numpy.arctan2(y, x))
    @staticmethod
    def _col_diff(y, x) :
        return numpy.divide(numpy.gradient(y), numpy.gradient(x))
    @staticmethod
    def _col_integ(y, x) :
        z = numpy.cumsum(
                numpy.multiply(
                    numpy.multiply(numpy.add(y[:-1], y[1:]), 0.5),
                    numpy.diff(x)
                )
            )
        return numpy.insert(z, 0, 0.0)
    @staticmethod
    def _col_eq(y, x) :
        return numpy.equal(y, x).astype(float)
    @staticmethod
    def _col_ne(y, x) :
        return numpy.not_equal(y, x).astype(float)
    @staticmethod
    def _col_ge(y, x) :
        return numpy.greater_equal(y, x).astype(float)
    @staticmethod
    def _col_le(y, x) :
        return numpy.less_equal(y, x).astype(float)
    @staticmethod
    def _col_gt(y, x) :
        return numpy.greater(y, x).astype(float)
    @staticmethod
    def _col_lt(y, x) :
        return numpy.less(y, x).astype(float)
    @staticmethod
    def _col_and(y, x) :
        return numpy.logical_and(y, x).astype(float)
    @staticmethod
    def _col_or(y, x) :
        return numpy.logical_or(y, x).astype(float)
    @staticmethod
    def _col_xor(y, x) :
        return numpy.logical_xor(y, x).astype(float)
    @staticmethod
    def _col_not(x) :
        return numpy.logical_not(x).astype(float)
    @staticmethod
    def datafile_format(file):
        """ determine data file format by examining top of file.

        **arguments**:

            .. option:: file

                data file to detect format

        **file types**:

            * nutmeg : binary or ascii spice output

            * csdf   : common simulator data format

            * hspice : tr or ac analysis output

            * csv : comma-separated values

            * ssv : space-separated values

        **examples**:

            >>> import decida.Data
            >>> data_format = decida.Data.Data.datafile_format("data.csv")
            >>> print data_format
            'csv'

            >>> from decida.Data import Data
            >>> data_format = Data.datafile_format("data.csv")
            >>> print data_format
            'csv'
        """
        #----------------------------------------------------------------------
        # files with an ascii header:
        #----------------------------------------------------------------------
        f = open(file, "r")
        lines = []
        for i in range(0, 20):
            line = f.readline()
            line = string.strip(line, "\r")
            line = string.strip(line, "\n")
            lines.append(line)
        f.close()
        #----------------------------------------------------------------------
        # nutmeg:
        #----------------------------------------------------------------------
        for line in lines :
            if re.search("Plotname:", line):
                return "nutmeg"
        #----------------------------------------------------------------------
        # csdf:
        #----------------------------------------------------------------------
        for line in lines :
            if re.search("^#H", line):
                return "csdf"
        #----------------------------------------------------------------------
        # hspice:
        #----------------------------------------------------------------------
        x = string.split(lines[0])
        if len(x) > 0:
            key = x[0]
            if len(key) == 20 and re.search("^[0-9]+$", key):
                return "hspice"
        #----------------------------------------------------------------------
        # csv:
        #----------------------------------------------------------------------
        if True :  # comment-lines are allowed
            line0 = None
            line1 = None
            for line in lines :
                if len(line) == 0 :
                    pass
                elif line[0] == "#" :
                    pass
                elif not line0:
                    line0 = line
                elif not line1:
                    line1 = line
        else :  # comment-lines are not allowed
            line0 = lines[0]
            line1 = lines[1]
        if re.search(",", line0):
            n1 = len(string.split(line0, ","))
            n2 = len(string.split(line1, ","))
            if n1 > 0 and n1 == n2:
                return "csv"
        #----------------------------------------------------------------------
        # ssv: comment-lines are allowed (20 lines enough?)
        #----------------------------------------------------------------------
        line0 = None
        line1 = None
        for line in lines :
            if len(line) == 0 :
                pass
            elif line[0] == "#" :
                pass
            elif not line0:
                line0 = line
            elif not line1:
                line1 = line
                n1 = len(string.split(line0))
                n2 = len(string.split(line1))
                if n1 > 0 and n1 == n2:
                    return "ssv"
        #----------------------------------------------------------------------
        # can't figure it out:
        #----------------------------------------------------------------------
        return None
    @staticmethod
    def nutmeg_blocks(datafile) :
        """ find number of data blocks in a nutmeg format data file.

        **arguments**:

            .. option:: datafile

                nutmeg format data file
        """
        f = open(datafile, "rb")
        block = -1
        blocks = []
        for line in f:
            if re.search("^Variables", line) :
                block += 1
                blocks.append(block)
        f.close()
        return(blocks)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # constructor, destructor, config
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #=========================================================================
    # METHOD: __init__
    # PURPOSE: constructor
    #=========================================================================
    def __init__(self, **kwargs) :
        ItclObjectx.__init__(self)
        #----------------------------------------------------------------------
        # private variables:
        #----------------------------------------------------------------------
        self._data_array = None
        self._data_col_names = []
        #----------------------------------------------------------------------
        # configuration options:
        #----------------------------------------------------------------------
        self._add_options({
            "verbose" : [False, None],
            "title"   : ["",    None],
        })
        #----------------------------------------------------------------------
        # keyword arguments are all configuration options
        #----------------------------------------------------------------------
        for key, value in kwargs.items() :
            self[key] = value
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # decida data built-in
    # methods use data array private data
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #=========================================================================
    # METHOD: show
    # PURPOSE: display data, str()
    #=========================================================================
    def show(self) :
        """ display Data information.

        **results**:

            * Display Data size, column names and data.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.show()
            number of rows:  10
            number of cols:  2
            column-names:    ['wc', 'freq']
            data: 
            [[ 11.9      4.017 ]
             [ 11.92     4.0112]
             [ 11.95     4.0026]
             [ 11.96     4.0005]
             [ 11.961    4.0004]
             [ 11.962    4.0002]
             [ 11.965    3.9987]
             [ 11.968    3.9976]
             [ 11.97     3.9974]
             [ 12.       3.9891]]

        """ 
        print " number of rows: ", self.nrows()
        print " number of cols: ", self.ncols()
        print " column-names:   ", self.names()
        print " data: "
        if self._data_array != None :
            print self._data_array.view()
    #=========================================================================
    # METHOD: twin
    # PURPOSE: display data in text-window
    #=========================================================================
    def twin(self) :
        """ display data in text-window.

        **results**:

            * Display data in a TextWindow object, with columns lined-up.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.twin()

        """
        lines = []
        lines.append(string.join(self.names()))
        for row in range(0, self.nrows()):
           line = []
           for col in range(0, self.ncols()):
               line.append(str(self.get_entry(row, col)))
           lines.append(string.join(line))
        lines = string.join(lines, "\n")
        tw = TextWindow(text_height=30, wait=False, destroy=False)
        tw.enter(lines)
        tw.lineup()
        tw.wait("dismiss")
        tw.__del__()
    #=========================================================================
    # METHOD: ncols
    # PURPOSE: return number of columns in data
    # NOTES:
    #   * may have appended columns to an empty array
    #=========================================================================
    def ncols(self) :
        """ return the number of columns in the data array.

        **results**:

            * Return the number of columns in the data array.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> print "number of columns = ", d.ncols()
            number of columns = 2

        """
        if (self._data_array == None) :
            return(len(self._data_col_names))
        elif len(self._data_array.shape) == 2 :
            return(self._data_array.shape[1])
        else :
            return(0)
    #=========================================================================
    # METHOD: nrows
    # PURPOSE: return number of rows in data
    #=========================================================================
    def nrows(self) :
        """ return the number of rows in the data array.

        **results**:

            * Return the number of rows in the data array.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> print "number of rows = ", d.nrows()
            number of rows = 12

        """
        if (self._data_array == None) :
            return(0)
        elif len(self._data_array.shape) == 2 :
            return(self._data_array.shape[0])
        else :
            return(0)
    #=========================================================================
    # METHOD: get_entry
    # PURPOSE: get a data entry
    #=========================================================================
    def get_entry(self, row, col) :
        """ get a data array entry.

        **arguments**:

            .. option::  row (int)

                the row in the data array

            .. option::  col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * Return the value in data array at the specified row and column.

        **notes**:

            * get_entry(0, col) returns the first row entry of col

            * get_entry(-1, col) returns the last row entry of col

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> temp = d.get_entry(1, "temp")

        """
        icol = self.index(col)
        if icol == None :
            self.warning("column not found")
            return(None)
        if row < -self.nrows() or row >= self.nrows() :
            self.warning("row index out of range")
            return(None)
        if icol < -self.ncols() or icol >= self.ncols() :
            self.warning("col index out of range")
            return(None)
        return(self._data_array[row, icol])
    #=========================================================================
    # METHOD: set_entry
    # PURPOSE: set a data entry
    #=========================================================================
    def set_entry(self, row, col, value) :
        """ set a data array entry.

        **arguments**:

            .. option::  row (int)

                the row in the data array

            .. option::  col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

            .. option::  value (float)

                the value to set the data array entry

        **results**:

            * The value in data array at the specified row and column is
              set to the specified value.
        
        **notes**:

            * set_entry(0, col, val) sets the first row entry of col

            * set_entry(-1, col, val) sets the last row entry of col


        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.set_entry(1, "temp", 45.0)

        """
        icol = self.index(col)
        if icol == None :
            self.warning("column \"%s\" not found" % (col))
            return(None)
        if row < -self.nrows() or row >= self.nrows() :
            self.warning("row index out of range")
            return(None)
        if icol < -self.ncols() or icol >= self.ncols() :
            self.warning("col index out of range")
            return(None)
        self._data_array[row, icol] = value
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # decida data.col built-in
    # methods use data array private data
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #=========================================================================
    # METHOD: dup
    # PURPOSE: create and copy data to a new data object
    #=========================================================================
    def dup(self) :
        """ create and copy data to a new Data object.

        **results**:

            * Returns a new Data object with the same data.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> dnew = d.dup()

        """
        d = Data()
        d["title"] = self["title"]
        d._data_array     = numpy.array(self._data_array, copy=True)
        d._data_col_names = self.names()
        return(d)
    #=========================================================================
    # METHOD: become
    # PURPOSE: copy data from another data object
    #=========================================================================
    def become(self, d) :
        """ copy data from another Data object.

        **arguments**:

            .. option:: d (Data)

                another Data object.

        **results**:

            * Replaces data array with copy of data array from the
              other Data object.
 
            * replace data array column names with names from the
              other Data object.

            * replace data title with title from the other Data object.

        **example**:

            >>> from decida.Data import Data
            >>> d2 = Data()
            >>> d2.read("data.csv")
            >>> d = Data()
            >>> d.become(d2)
        """
        self["title"] = d["title"]
        self._data_array     = numpy.array(d._data_array, copy=True)
        self._data_col_names = d.names()
    #=========================================================================
    # METHOD: edit
    # PURPOSE: make array editable
    #=========================================================================
    def edit(self) :
        """ make array editable.

        **notes**:

            * in some cases the data array comes up read-only

            * flag the data array as editable

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.edit()

        """
        self._data_array.setflags(write=True)
    #=========================================================================
    # METHOD: index
    # PURPOSE: find column index of column named col or trial col index = col
    #=========================================================================
    def index(self, col) :
        """ find column index of column named col or trial col index = col.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * return int corresponding to the column index in the data array

            * if column name not found, return None

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> itemp = d.index("temp")

        """
        if   type(col) == int :
            try :
                xcol = self._data_col_names[col]
                index = col
            except IndexError :
                index = None
        elif type(col) == str :
            try :
                index = self._data_col_names.index(col)
            except ValueError :
                index = None
        else :
            index = None
            self.warning("column must be str or int: " + str(col))
        return(index)
    #=========================================================================
    # METHOD: name
    # PURPOSE: get or set column name
    #=========================================================================
    def name(self, col, name=None) :
        """ get or set column name.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array.
                If col is a string, it refers to the column named col.

            .. option:: name (str, default=None)

                the name to assign to column col.  If name is None,
                return the name of column col.

        **results**:

            * If name is not None, rename column col to name

            * If name is None, return the column name of column col

            * If column col not found, print warning, return None

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> print "column %d = %s" % (1, d.name(1))
            column 1 = freq

        """
        index = self.index(col)
        if index == None :
            self.warning("column not found in data: " + str(col))
            return
        if name == None :
            return(self._data_col_names[index])
        else :
            self._data_col_names[index] = name
    #=========================================================================
    # METHOD: names
    # PURPOSE: return list of column names
    # NOTES:
    #   * returned list is a copy of the column names
    #=========================================================================
    def names(self) :
        """ return list of column names.

        **results**:

            * Returns a list of Data column names.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> print "columns = ", d.names()
            columns = ['wc', 'freq']

        """
        cols = list(self._data_col_names)
        return(cols)
    #=========================================================================
    # METHOD: unique_name
    # PURPOSE: come up with a unique column name with the given prefix
    #=========================================================================
    def unique_name(self, prefix="z") :
        """ come up with a unique column name with the given prefix.

        **arguments**:

            .. option:: prefix (str, default="z")

                prefix of a trial column name.

        **results**:

            * Returns a trial column name which isn't in the list of
              existing column names.

            * First tries prefix as a unique column name.  If that column
              already exists, try prefix + "_" + str(int), where int is
              incremented until a the trial column name isn't already present
              in the data array names. If int is > 10000, give up.

            * The trial name is *not* used yet to create a new data column.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> new_col = d.unique_name("z")
            'z_1'

        """
        name = prefix
        i = 0
        while name in self.names() :
            if i > 10000:
                self.fatal("not able to come up with unique name")
            i += 1
            name = prefix + "_" + str(i)
        return name
    #=========================================================================
    # METHOD: append
    # PURPOSE: append empty (0.0) columns if not already present
    #=========================================================================
    def append(self, *cols) :
        """ append empty (0.0) columns if not already present.

        **arguments**:

            .. option:: cols (tuple)

               list of column names or lists of column names.

        **results**:

            * A list of column names is developed by flattening the cols
              argument(s).

            * For each column name in the column list, if the column
              isn't already present, add a new column at the end of the
              data array.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.append("t12", "t13", ("t15", "t18"))

        """
        col_list = []
        for col in cols :
            if type(col) in (TupleType, ListType) :
                col_list.extend(col)
            elif col is not None:
                col_list.append(col)
        ic = self.ncols() - 1
        for col in col_list :
            if self.index(col) == None :
                ic += 1
                if self._data_array != None :
                    c = numpy.insert(self._data_array, ic, 0.0, axis=1)
                    self._data_array = c
                self._data_col_names.insert(ic, col)
    #=========================================================================
    # METHOD: insert
    # PURPOSE: insert empty columns after col_before
    #=========================================================================
    def insert(self, col_before, *cols) :
        """ insert empty columns after col_before.

        **arguments**:

            .. option:: col_before (int or str)

               existing column (index or name) to insert column after.

            .. option:: cols (tuple)

               list of column names or lists of column names.

        **results**:

            * A list of column names is developed by flattening the cols
              argument(s).

            * If col_before doesn't exist, return without doing anything.

            * For each column name in the column list, if the column
              isn't already present, add a new column at the end of the
              data array.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.insert("gm", "t12", "t13", ("t15", "t18"))

        """
        col_list = []
        for col in cols :
            if type(col) in (TupleType, ListType) :
                col_list.extend(col)
            elif col is not None:
                col_list.append(col)
        ic = self.index(col_before)
        if ic == None :
            self.warning("column " + col_before + " doesn't exist")
            return
        for col in col_list :
            if self.index(col) == None :
                ic += 1
                if self._data_array != None :
                    c = numpy.insert(self._data_array, ic, 0.0, axis=1)
                    self._data_array = c
                self._data_col_names.insert(ic, col)
    #=========================================================================
    # METHOD: delete
    # PURPOSE: delete columns if present
    #=========================================================================
    def delete(self, *cols) :
        """ delete columns if present.

        **arguments**:

            .. option:: cols (tuple)

               list of column names or lists of column names.

        **results**:

            * A list of column names is developed by flattening the cols
              argument(s).

            * For each column name in the column list, if the column
              is present, delete it from the data array.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.delete("t12", "t13", ("t15", "t18"))

        """
        col_list = []
        for col in cols :
            if type(col) in (TupleType, ListType) :
                col_list.extend(col)
            elif col is not None:
                col_list.append(col)
        if len(col_list) < 1 : return
        ics = []
        for col in col_list :
            ic = self.index(col)
            if ic != None :
                ics.append(ic)
        c = numpy.delete(self._data_array, ics, axis=1)
        self._data_array = c
        c = filter(lambda col: self.index(col) not in ics, self.names())
        self._data_col_names = c
    #=========================================================================
    # METHOD: select
    # PURPOSE: delete columns which aren't selected
    #=========================================================================
    def select(self, *cols) :
        """ delete columns which aren't selected.

        **arguments**:

            .. option:: cols (tuple)

               list of column names or lists of column names.

        **results**:

            * A list of column names is developed by flattening the cols
              argument(s).  Add to this list complex columns
              REAL, IMAG, MAG, DB, PH for each selected column
              (REAL(col), etc.)

            * For each column in the data array, if it is not in the 
              column list, delete it from the data array.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.select("time", "V(zout)")

        """
        col_list = []
        for col in cols :
            if type(col) in (TupleType, ListType) :
                col_list.extend(col)
            elif col is not None:
                col_list.append(col)
        cols_to_keep = []
        for col in col_list :
            cols_to_keep.append(col)
            for cx in ("REAL", "IMAG", "MAG", "DB", "PH") :
                cols_to_keep.append("%s(%s)" % (cx, col))
        cols_to_delete = []
        for col in self.names() :
            if not col in cols_to_keep :
                cols_to_delete.append(col)
        self.delete(cols_to_delete)
    #=========================================================================
    # METHOD: append_data
    # PURPOSE: append data columns
    #=========================================================================
    def append_data(self, data1) :
        """ append data columns from another Data object.

        **arguments**:

            .. option:: data1 (Data)

               Another Data object with the same number of rows as this
               Data object.

        **results**:

            * Does not ensure that data column names don't collide

            * data1 is concatenated to this Data object.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d1 = Data()
            >>> d1.read("data1.csv")
            >>> d.append_data(d1)

        """
        if not isinstance(data1, Data) :
            self.fatal("data1 is not a data object")
        if data1.nrows() != self.nrows() :
            self.fatal("incompatible data (different number of rows)")
        c = numpy.concatenate((self._data_array, data1._data_array), axis=1)
        self._data_array = c
        for col in data1.names() :
            self._data_col_names.append(col)
    #=========================================================================
    # METHOD: get
    # PURPOSE: return column vector
    #=========================================================================
    def get(self, col) :
        """ return column vector.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * Feturn (numpy) vector of values in the data array column.

            * If col is not present in the data array, print warning.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.get("gds")

        """
        index = self.index(col)
        if index == None :
            self.warning("array column " + str(col) + " not found")
            return(None)
        return(self._data_array[:,index])
    #=========================================================================
    # METHOD: set_parsed
    # PURPOSE: basic column operations on parsed equation
    #=========================================================================
    def set_parsed(self, equation) :
        """ basic column operations on parsed equation.
        
        **arguments**:

            .. option:: equation (str)

                An equation which has been parsed into space-separated
                tokens. Data.set() uses Data.set_parsed() after
                parsing equations into a set of parsed equations.

        **results**:

            * The left-hand-side variable (lhsvar) is the first token.

            * The equals sign is the second token.

            * The following tokens are the right-hand side expression.

            * If the right-hand-side expression has 1 token:

                * If the rhs is another variable, rhsvar, which is already
                  present in the data array, set lhsvar to rhsvar.

                * If the rhs is a real number, rnum,
                  set lhsvar to rnum.

                * If the rhs is one of the following constants, set the lhsvar
                  to the value of the constant.

                  * pi   : 3.14159 ...

                  * e0   : 8.854215e-14

                  * qe   : 1.602192e-19

                  * kb   : 1.380622e-23

                  * kbev : 8.61708e-5

                  * tabs : 273.15

                * If the rhs is "index", set the lhsvar to the row index
                  (0 to nrows-1).

            * If the right-hand-side expression has 2 tokens (unary operation):

                * The first token is the unary operation.

                * The second token is either
                  another variable already in the array, or a real number.
 
                * Set lhsvar to the unary operation of
                  the right-hand side.

                * Supported unary operations are:
                  - sign reciprocal sqrt square abs sin cos tan
                  asin acos atan exp expm1 exp2 log log10 log2 log1p
                  sinh cosh tanh asinh acosh atanh degrees radians
                  deg2rad rad2deg rint fix floor ceil trunc

            * If the right-hand-side expression has 3 tokens (binary operation):

                * The first token is the first operand

                * The second token is the binary operation

                * The third token is the second operand

                * The two operands can be either
                  other variables already in the array, or real numbers.

                * Set lhsvar to the binary operation
                  of the two operands.

                * Supported binary operations are:
                  + - * / ^ true_divide floor_divide fmod mod rem hypot max min

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.set_parsed("z = sqrt gout")
            >>> d.set_parsed("z = zout + z")
            >>> d.set_parsed("z = abs z")

        """
        m=re.search("^([^=]+)=(.+)$", equation)
        if not m :
            self.warning("equation not in right format: LHS = RHS")
            return
        col = m.group(1)
        rhs = m.group(2)
        col = string.strip(col)
        rhs = string.strip(rhs)
        tok = string.split(rhs)
        index = self.index(col)
        Constants = {
            "pi"   : math.acos(-1),
            "e0"   : 8.854215e-14,
            "qe"   : 1.602192e-19,
            "kb"   : 1.380622e-23,
            "kbev" : 8.61708e-5,
            "tabs" : 273.15,
        }
        if index == None :
            self.append(col)
            index = self.index(col)
        if   len(tok) == 1:
            xc = tok[0]
            if   xc in self.names() :
                x = self.get(xc)
            elif xc in Constants :
                x = Constants[xc]
            elif xc == "index" :
                x = range(0, self.nrows())
            else :
                x = string.atof(xc)
            self._data_array[:,index] = x
        elif len(tok) == 2:
            op, xc = tok
            if   xc in self.names() :
                x = self.get(xc)
            elif xc in Constants :
                x = Constants[xc]
            else :
                x = string.atof(xc)
            if op in Data._UnaryOp :
                self._data_array[:,index] = Data._UnaryOp[op](x)
            elif op in Data._UnaryOpD :
                func = eval("Data." + Data._UnaryOpD[op])
                self._data_array[:,index] = func(x)
            else :
                self.warning("unary operation not supported: " + op)
        elif len(tok) == 3:
            yc, op , xc = tok
            if   xc in self.names() :
                x = self.get(xc)
            elif xc in Constants :
                x = Constants[xc]
            else:
                x = string.atof(xc)
            if   yc in self.names() :
                y = self.get(yc)
            elif yc in Constants :
                y = Constants[yc]
            else :
                y = string.atof(yc)
            if   op in Data._BinaryOp :
                self._data_array[:,index] = Data._BinaryOp[op](y, x)
            elif op in Data._BinaryOpD :
                func = eval("Data." + Data._BinaryOpD[op])
                self._data_array[:,index] = func(y, x)
            else :
                self.warning("binary operation not supported: " + op)
        else :
            self.warning("can't interpret equation:\n  %s" % (equation))
    #=========================================================================
    # METHOD: max
    # PURPOSE: maximum value in column
    #=========================================================================
    def max(self, col) :
        """ maximum number in column.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * return maximum value in column col.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> vmax = d.max("v(z)")

        """
        max = numpy.amax(self.get(col))
        return(max)
    #=========================================================================
    # METHOD: min
    # PURPOSE: minimum value in column
    #=========================================================================
    def min(self, col) :
        """ minimum number in column.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * return minimum value in column col.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> vmin = d.min("v(z)")

        """
        min = numpy.amin(self.get(col))
        return(min)
    #=========================================================================
    # METHOD: mean
    # PURPOSE: mean of column
    #=========================================================================
    def mean(self, col) :
        """ mean of column.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * return meanvalue in column col.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> vavg = d.mean("v(z)")

        """
        mean = numpy.mean(self.get(col))
        return(mean)
    #=========================================================================
    # METHOD: median
    # PURPOSE: median of column
    #=========================================================================
    def median(self, col) :
        """ median of column.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * return median value in column col.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> vmed = d.median("v(z)")

        """
        median = numpy.median(self.get(col))
        return(median)
    #=========================================================================
    # METHOD: var
    # PURPOSE: variance of column
    #=========================================================================
    def var(self, col) :
        """ variance of column.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * return variance in column col.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> vvar = d.var("v(z)")

        """
        var= numpy.var(self.get(col))
        return(var)
    #=========================================================================
    # METHOD: std
    # PURPOSE: standard-deviation of column
    #=========================================================================
    def std(self, col) :
        """ standard-deviation of column.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * return standard-deviation in column col.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> vstd = d.std("v(z)")

        """
        std= numpy.std(self.get(col))
        return(std)
    #=========================================================================
    # METHOD: unique
    # PURPOSE: return unique numbers in column
    #=========================================================================
    def unique(self, col) :
        """ return unique numbers in column.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

        **results**:

            * return unique values in column col.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> values = d.unique("v(z)")

        """
        values = numpy.unique(self.get(col))
        return(values)
    #=========================================================================
    # METHOD: offset
    # PURPOSE: column offset
    #=========================================================================
    def __offset(self, col, col1, step_value, col_list) :
        """ column offset. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: range
    # PURPOSE: column range
    #=========================================================================
    def __range(self, col, row1, row2) :
        """ column range. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: linreg
    # PURPOSE: linear regression
    #=========================================================================
    def linreg(self, xcol, ycol) :
        """ linear regression.

        **arguments**:

            .. option:: xcol (int or str)

                x values of data to regress.
                If xcol is a string, it refers to the column named xcol.

            .. option:: ycol (int or str)

                y values of data to regress.
                If ycol is a string, it refers to the column named ycol.

        **results**:

            * Calculate linear regression of data points x, y.

            * Return dictionary of :
              "report" : regression line equation.
              "coefficients" : list of y-intercept and slope of the regression line.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> V = d.linreg("xvalues", "yvalues")
            >>> yint, slope = V["coefficients"]
            >>> print = V["report"]

        """
        if not xcol in self.names() :
            self.warning("x-column \"%s\" is not in data" % (xcol))
            return
        if not ycol in self.names() :
            self.warning("y-column \"%s\" is not in data" % (ycol))
            return
        s1, s2, r1, r2 = 0.0, 0.0, 0.0, 0.0
        npts = self.nrows()
        for i in range(0, npts) :
            x = self.get_entry(i, xcol)
            y = self.get_entry(i, ycol)
            s1 += x
            s2 += x*x
            r1 += y
            r2 += x*y
        r  = npts*s2 - s1*s1
        if r == 0 :
            self.warning("linear regression matrix is singular")
            return
        b0 = (  s2*r1 - s1*r2)/r
        b1 = (npts*r2 - s1*r1)/r
        olines = []
        olines.append("%s =" % (ycol))
        olines.append("   %10.3e" % (b0))
        olines.append(" + %10.3e * %s" % (b1, xcol))
        report = string.join(olines, "\n")
        Vret = {}
        Vret["coefficients"] = (b0, b1)
        Vret["report"] = report
        return Vret
    #=========================================================================
    # METHOD: quadreg
    # PURPOSE: quadradic regression
    #=========================================================================
    def quadreg(self, xcol, ycol) :
        """ quadradic regression.

        **arguments**:

            .. option:: xcol (int or str)

                x values of data to regress.
                If xcol is a string, it refers to the column named xcol.

            .. option:: ycol (int or str)

                y values of data to regress.
                If ycol is a string, it refers to the column named ycol.

        **results**:

            * Calculate quadradic regression of data points x, y.

            * Return dictionary of :
              "report" : regression curve equation.
              "coefficients" : list of coefficients of the regression curve, b0 + b1*x + b2*x^2

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> V = d.quadreg("xvalues", "yvalues")
            >>> print = V["report"]
            >>> b0, b1, b2 = V["coefficients"]

        """
        if not xcol in self.names() :
            self.warning("x-column \"%s\" is not in data" % (xcol))
            return
        if not ycol in self.names() :
            self.warning("y-column \"%s\" is not in data" % (ycol))
            return
        s1, s2, s3, s4, r1, r2, r3 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        npts = self.nrows()
        for i in range(0, npts) :
            x = self.get_entry(i, xcol)
            y = self.get_entry(i, ycol)
            s1 += x
            s2 += x*x
            s3 += x*x*x
            s4 += x*x*x*x
            r1 += y
            r2 += x*y
            r3 += x*x*y
        a11 = float(npts)
        a12, a21 = s1, s1
        a13, a22, a31 = s2, s2, s2
        a23, a32 = s3, s3
        a33 = s4
        if a11 == 0.0 :
            self.warning("quadradic regression matrix is singular")
            return
        r    = a21/ a11
        a22 -= a12*r
        a23 -= a13*r
        r2  -= r1*r
        r    = a31/ a11
        a32 -= a12*r
        a33 -= a13*r
        r3  -= r1*r
        if a22 == 0.0 :
            self.warning("quadradic regression matrix is singular")
            return
        r    = a32 / a22
        a33 -= a23*r
        r3  -= r2*r
        if a33 == 0.0 :
            self.warning("quadradic regression matrix is singular")
            return
        b2 = r3/a33
        b1 = (r2 - b2*a23)/a22
        b0 = (r1 - b2*a13 - b1*a12)/a11
        olines = []
        olines.append("%s =" % (ycol))
        olines.append("   %10.3e" % (b0))
        olines.append(" + %10.3e * %s" % (b1, xcol))
        olines.append(" + %10.3e * %s^2" % (b2, xcol))
        report = string.join(olines, "\n")
        Vret = {}
        Vret["coefficients"] = (b0, b1, b2)
        Vret["report"] = report
        return Vret
    #=========================================================================
    # METHOD: fourcoeff
    # PURPOSE: fourier coefficients
    #=========================================================================
    def fourcoeff(self, xcol, ycol, nfour=8) :
        """ fourier coefficients.

        **arguments**:

            .. option:: xcol (int or str)

                time column.
                If xcol is a string, it refers to the column named xcol.

            .. option:: ycol (int or str)

                signal column.
                If ycol is a string, it refers to the column named ycol.

            .. option:: nfour (int, default=8)

                number of harmonics.

        **results**:

            * Return dictionary of :

              "report" : report Fourier expansion in terms of the basis functions
              sin(n*2*pi*xcol/T) and cos(n*2*pi*xcol/T),
              where T is the maximum - minimum of the time column (xcol).
              The report also includes the equivalent Fourier expansion in terms of
              coeff*sin(2*pi*xcol/T + phase)

              "coefficients" : list of fourier coefficients of cosine and sine basis functions

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> V = d.nfour("time", "v(z)", nfour=8)
            >>> print V["report"]

        """
        if not xcol in self.names() :
            self.warning("x-column \"%s\" is not in data" % (xcol))
            return
        if not ycol in self.names() :
            self.warning("y-column \"%s\" is not in data" % (ycol))
            return
        xmax = self.max(xcol)
        xmin = self.min(xcol)
        T    = xmax - xmin
        pi   = math.acos(-1)
        Basis = {}
        tmpcols=[]
        wto  = self.unique_name("wto")
        self.set("%s = 2*%g*%s/%g" % (wto, pi, xcol, T))
        tmpcols.append(wto)
        for n in range(1, nfour+1) :
            cn = self.unique_name("cos_%d" % (n))
            sn = self.unique_name("sin_%d" % (n))
            self.set("%s = cos(%d*%s)" % (cn, n, wto))
            self.set("%s = sin(%d*%s)" % (sn, n, wto))
            tmpcols.append(cn)
            tmpcols.append(sn)
            Basis["cos_%d" % (n)] = cn
            Basis["sin_%d" % (n)] = sn
        #----------------------------------------------------------------------
        # fourier coefficients
        #----------------------------------------------------------------------
        olist  = []
        olines = []
        olines2 = []
        integ = self.unique_name("integ")
        tmpcols.append(integ)
        self.set("%s = integ(%s, %s)" % (integ, ycol, xcol))
        f0 = self.get_entry(-1, integ) / T
        olist.append(f0)
        olines.append("%s =" % (ycol))
        olines.append("   %10.3e" % (f0))
        olines2.append(" = %10.3e" % (f0))
        for n in range(1, nfour+1) :
            cn = Basis["cos_%d" % (n)]
            sn = Basis["sin_%d" % (n)]
            self.set("%s = integ(%s*%s, %s)" % (integ, ycol, cn, xcol))
            fc = 2 * self.get_entry(-1, integ) / T
            self.set("%s = integ(%s*%s, %s)" % (integ, ycol, sn, xcol))
            fs = 2 * self.get_entry(-1, integ) / T
            fa = math.sqrt(fc*fc + fs*fs)
            fp = math.atan2(fc, fs)
            olist.append(fc)
            olist.append(fs)
            olines.append(" + %10.3e * cos(%d*2*PI*%s/T)" % (fc, n , xcol))
            olines.append(" + %10.3e * sin(%d*2*PI*%s/T)" % (fs, n , xcol))
            olines2.append(" + %10.3e * sin(%d*2*PI*%s/T + %s)" % (fa, n, xcol, fp))
        self.delete(tmpcols)
        olines.extend(olines2)
        report = string.join(olines, "\n")
        Vret = {}
        Vret["coefficients"] = (olist)
        Vret["report"] = report
        return Vret
    #=========================================================================
    # METHOD: splint
    # PURPOSE: spine interpolation
    #=========================================================================
    def __splint(self, xvalue, xcol, ycol, d2y_dx2_col) :
        """ spine interpolation. (not yet done)"""
        pass
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # decida data.row built-in
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #=========================================================================
    # METHOD: row_append
    # PURPOSE: append empty (0.0) rows
    #=========================================================================
    def row_append(self, number=1) :
        """ append empty (0.0) rows.

        **arguments**:

            .. option:: number (int, default=1)

               number of rows to append.

        **results**:

            * Append rows to data array.

            * Each data entry is set to 0.0.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.row_append(2)

        """
        for row in range(self.nrows(), self.nrows() + number) :
            if self._data_array == None :
                if self.ncols() != 0 :
                    r = numpy.zeros((1, self.ncols()), dtype="float64")
                    self._data_array = r
                else :
                    print "cannot add rows to an array with no columns"
                    return
            else :
                r = numpy.insert(self._data_array, row, 0.0, axis=0)
                self._data_array = r
    #=========================================================================
    # METHOD: row_get
    # PURPOSE: get row vector
    #=========================================================================
    def row_get(self, row) :
        """ get row vector.

        **arguments**:

            .. option:: row (int)

               The row index.

        **results**:

            * Return row of values from specified row.

            * If row index is out of range, print warning.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.row_get(7)

        """
        if row < -self.nrows() or row >= self.nrows() :
            print "row index out of range"
            return(None)
        else :
            return(self._data_array[row, :])
    #=========================================================================
    # METHOD: row_set
    # PURPOSE: set row vector
    #=========================================================================
    def row_set(self, row, row_vector) :
        """ set row vector.

        **arguments**:

            .. option:: row (int)

               The row index.

            .. option:: row_vector (array-like: list, tuple, or numpy array)

               Vector of values to set row entries.

        **results**:

            * Values in specified row are set to specified vector.

            * If row index is out of range, print warning.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.row_set(3, (2.3, 3.3))

        """
        if row < -self.nrows() or row >= self.nrows() :
            print "row index out of range"
        else :
            self._data_array[row, :] = row_vector
    #=========================================================================
    # METHOD: row_append_data
    # PURPOSE: append data rows
    #=========================================================================
    def row_append_data(self, data1) :
        """ append data rows from another Data object.

        **arguments**:

            .. option:: data1 (Data)

               Another Data object with the same number of columns as this
               Data object.

        **results**:

            * Does not ensure that Data column names don't collide.

            * data1 is concatenated to this data object.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d1 = Data()
            >>> d1.read("data1.csv")
            >>> d.row_append_data(d1)

        """
        if not isinstance(data1, Data) :
            self.fatal("data1 is not a data object")
        if data1.ncols() != self.ncols() :
            self.fatal("incompatible (different number of columns)")
        c = numpy.concatenate((self._data_array, data1._data_array), axis=0)
        self._data_array = c
    #=========================================================================
    # METHOD:  filter
    # PURPOSE: delete rows if column condition not true
    #=========================================================================
    def filter(self, condition) :
        """ delete rows if column condition not true.

        **arguments**:

            .. option:: condition (str)

                 a boolean expression of data columns

        **results**:

            * Remove all data rows where the condition evaluates False.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.filter("time > 10e-9")

        """
        if True :
            condition = decida.interpolate(condition, 2)
        z = self.unique_name()
        self.set("%s = %s" % (z, condition))
        b = numpy.where(numpy.not_equal(self.get(z), 1))
        self._data_array = numpy.delete(self._data_array, b, 0)
        self.delete(z)
    #=========================================================================
    # METHOD:  set
    # PURPOSE: parse and evaluate an equation
    #=========================================================================
    def set(self, eqn) :
        """ parse and evaluate an equation.

        **arguments**:

            .. option:: eqn (str)

               Equation to evaluate.
               The equation must include a left-hand-side variable, an
               equals and a right-hand-side expression.

        **results**:

            * The equation string eqn is first interpolated to substitute
              frame variable values into the eqn string. 

            * Any existing variables are interpolated into the
              right-hand-side expression.  For example if x1
              is present in the data array, the reference x1
              in the right-hand-side expression is to the variable
              x1.

            * the equation is parsed and evaluated using Data.set_parsed.

            * The left-hand-side variable is
              added to the data array if not already present.  If already
              present, it is replaced with the calculated results.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.names()
            'freq V(out_p) V(out_n)'
            >>> vref = 1.5
            >>> d.set("out_dm = V(out_p) - V(out_n)")
            >>> d.set("out_cm = 0.5*(V(out_p) + V(out_n))")
            >>> d.set("dif_cm = out_cm - $vref")

        """
        if True :
            eqn   = decida.interpolate(eqn, 2)
        ep    = EquationParser(eqn, varlist=self.names(), debug=False)
        eqns  = ep.parse()
        ivars = ep.ivars()
        del ep
        if False :
            for eqn in eqns :
                print eqn
        for eqn in eqns :
            self.set_parsed(eqn)
        self.delete(ivars)
    #=========================================================================
    # METHOD:  cxset
    # PURPOSE: parse and evaluate an equation (complex)
    #=========================================================================
    def cxset(self, eqn) :
        """ parse and evaluate an equation with complex variables.

        **arguments**:

            .. option:: eqn (str)

               Equation to evaluate.
               The equation must include a left-hand-side variable, an
               equals and a right-hand-side expression.

        **results**:

            * The equation string eqn is first interpolated to substitute
              frame variable values into the eqn string. 

            * Any existing complex variables are interpolated into the
              right-hand-side expression.  For example if REAL(x1) and
              IMAG(x1) are present in the data array, the reference x1
              in the right-hand-side expression is to the complex variable
              x1.

            * the equation is parsed and evaluated using Data.cxset_parsed.

            * The left-hand-side variable REAL() and IMAG() components
              are added to the data array if not already present.  If already
              present, they are replaced with the calculated results.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.names()
            'freq REAL(gout) IMAG(gout) REAL(zout) IMAG(zout)'
            >>> vz = 3.3
            >>> d.cxset("z = gout + zout + $vz")
            >>> d.names()
            'freq REAL(gout) IMAG(gout) REAL(zout) IMAG(zout) REAL(z) IMAG(z)'

        """
        varlist = []
        for name in self.names() :
            m = re.search("^(REAL|IMAG|MAG|DB|PH)\((.+)\)$", name)
            if m :
                mod = m.group(1)
                var = m.group(2)
                if not var in varlist:
                    varlist.append(var)
                varlist.append(name)
            else :
                varlist.append(name)
        if True :
            eqn   = decida.interpolate(eqn, 2)
        ep    = EquationParser(eqn, varlist=varlist, debug=False)
        eqns  = ep.parse()
        ivars = ep.ivars()
        ivarlist = []
        for var in ivars :
            for mod in ("REAL", "IMAG", "MAG", "DB", "PH") :
                ivarlist.append("%s(%s)" % (mod, var))
        del ep
        if False :
            for eqn in eqns :
                print eqn
        for eqn in eqns :
            self.cxset_parsed(eqn)
        self.delete(ivarlist)
    #=========================================================================
    # METHOD: sort
    # PURPOSE: sort according to cols
    # NOTES:
    #   * cols can contain list of column names: gets flattened
    #=========================================================================
    def sort(self, *cols) :
        """ sort according to cols.

        **arguments**:

            .. option:: cols (tuple)

               list of column names or lists of column names.

        **results**:

            * Data is re-ordered such that data entries in the
              specified columns and rows run in ascending numerical order.

            * If more than one column is specified, for each set of constant
              first specified columns, data for the last specified column
              runs in ascending order.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.show()
            number of rows:  10
            number of cols:  2
            column-names:    ['wc', 'freq']
            data: 
            [[ 11.9      4.017 ]
             [ 11.92     4.0112]
             [ 11.95     4.0026]
             [ 11.96     4.0005]
             [ 11.961    4.0004]
             [ 11.962    4.0002]
             [ 11.965    3.9987]
             [ 11.968    3.9976]
             [ 11.97     3.9974]
             [ 12.       3.9891]]
            >>> d.sort("freq")
            >>> d.show()
            number of rows:  10
            number of cols:  2
            column-names:    ['wc', 'freq']
             data: 
            [[ 12.       3.9891]
             [ 11.97     3.9974]
             [ 11.968    3.9976]
             [ 11.965    3.9987]
             [ 11.962    4.0002]
             [ 11.961    4.0004]
             [ 11.96     4.0005]
             [ 11.95     4.0026]
             [ 11.92     4.0112]
             [ 11.9      4.017 ]]
        """
        col_list = []
        for col in cols :
            if type(col) in (TupleType, ListType) :
                col_list.extend(col)
            elif col is not None:
                col_list.append(col)
        keys = []
        for col in col_list :
            a = self.get(col)
            keys.append(a)
        keys.reverse()
        ind = numpy.lexsort(keys)
        dnew = Data()
        for col in self.names() :
            dnew.append(col)
        for row in ind :
            dnew.row_append()
            dnew.row_set(-1, self.row_get(row))
        self._data_array = dnew._data_array
        del dnew
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # decida data library
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #=========================================================================
    # METHOD: crossings
    # PURPOSE: xcol values when ycol crosses level
    #=========================================================================
    def crossings(self, xcol, ycol, level=0, edge="both") :
        """ xcol values when ycol crosses level.

        **arguments**:

            .. option:: xcol (int or str)

                x-column to use for crossing values.
                If xcol is a string, it refers to the column named xcol.

            .. option:: ycol (int or str)

                y-column to use for crossing values.
                If ycol is a string, it refers to the column named ycol.

            .. option::  level (float, default=None)

                signal crossing level to use.  If level is None, use
                0.5*(max(ycol) + min(ycol))

            .. option::  edge (str, default="both")

                signal edge(s) to use to accumulate crossings.
                values must be in ("rising", "falling", "both")

        **results**:

            * Returns a list of xcol crossings of edge of ycol of level.

            * Crossing values are linearly-interpolated.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> ycrossings = d.crossings("time", "v(out)", level=0.4)

        """
        xvals = self.get(xcol)
        yvals = numpy.subtract(self.get(ycol), level)
        a     = numpy.diff(numpy.sign(yvals))
        icross = numpy.where(a)[0]
        crossings=[]
        for i in icross :
           x0, x1 = xvals[i: i+2]
           y0, y1 = yvals[i: i+2]
           cross  = float(x0-y0*(x1-x0)/(y1-y0))
           if   edge == "both" :
               crossings.append(cross)
           elif edge == "rising"  and (y1 >= 0) :
               crossings.append(cross)
           elif edge == "falling" and (y1 <  0) :
               crossings.append(cross)
           elif edge == "transitions" :
               if (y1 >= 0) :
                   crossings.append([cross, 1])
               else :
                   crossings.append([cross, 0])
        return(crossings)
    #=========================================================================
    # METHOD: periods
    # PURPOSE: find period, freq, duty-cycle list
    # RETURNS: data object
    # NOTES:
    #   * formerly duty_cycle
    #   * doesn't interpolate other columns yet
    #   * needs min, max, row_append
    #=========================================================================
    def periods(self, xcol, ycol, level=None) :
        """ find period, freq, duty-cycle list.

        **arguments**:

            .. option:: xcol (int or str)

                time column.
                If xcol is a string, it refers to the column named xcol.

            .. option:: ycol (int or str)

                signal column.
                If ycol is a string, it refers to the column named ycol.

            .. option::  level (float, default=None)

                signal crossing level to use.  If level is None, use
                0.5*(max(ycol) + min(ycol))

        **results**:

            * Returns a Data object with frequency, period and duty_cycle 
              columns.  These are calculated at each signal crossing of
              level.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d1 = d.periods("time", "v(out)", level=0.4)

        """
        if level == None :
            ymax = self.max(ycol)
            ymin = self.min(ycol)
            level = 0.5*(ymax+ymin)
        crossings = self.crossings(
           xcol=xcol, ycol=ycol, level=level, edge="transitions")
        d=Data()
        d.append("time", "frequency", "period", "duty_cycle")
        start = True
        for time, edge in crossings :
            if edge == 0 :
                t1 = time
            elif start :
                t2 = time
                start = False
            else :
                t0 = t2
                t2 = time
                period = t2 - t0
                if period > 0.0 :
                    frequency  = 1.0/period
                    duty_cycle = 100.0*(t1-t0)*frequency
                else :
                    frequency  = 0.0
                    duty_cycle = 0.0
                d.row_append()
                d.set_entry(-1, "time", t2)
                d.set_entry(-1, "frequency", frequency)
                d.set_entry(-1, "period", period)
                d.set_entry(-1, "duty_cycle", duty_cycle)
        return(d)
    #=========================================================================
    # METHOD: delays
    # PURPOSE: return list of delays between sig1 and sig2
    # NOTES :
    #     * sig2 has fewer transitions than sig1
    #     * for each sig2 transition, find first preceding sig1 transition
    #     * return difference
    #=========================================================================
    def delays(self, time, sig1, sig2,
        level=0.0, level2=None, edge="rising", edge2=None
    ) :
        if  level2 is None :
            level2 = level
        if  edge2 is None :
            edge2 = edge
        t1s = self.crossings(time, sig1, level,  edge=edge)
        t2s = self.crossings(time, sig2, level2, edge=edge)
        delays = []
        if len(t1s) > 0 :
            t1  = t1s.pop(0)
            t1l = t1
            for t2 in t2s :
                while t1 < t2 and len(t1s) > 0 :
                    t1l = t1
                    t1  = t1s.pop(0)
                if t2 >= t1l :
                    delays.append(t2-t1l)
        return delays
    #=========================================================================
    # METHOD: skews
    # PURPOSE: return list of skews between sig1 and sig2
    # NOTES :
    #     * foreach sig2 transition, find closest of preceding or 
    #         following sig1 transition
    #     * return difference
    #=========================================================================
    def skews(self, time, sig1, sig2,
        level=0.0, level2=None, edge="rising", edge2=None
    ) :
        if  level2 is None :
            level2 = level
        if  edge2 is None :
            edge2 = edge
        t1s = self.crossings(time, sig1, level,  edge=edge)
        t2s = self.crossings(time, sig2, level2, edge=edge)
        skews = []
        if len(t1s) > 0 :
            t1  = t1s.pop(0)
            t1l = t1
            for t2 in t2s :
                while t1 < t2 and len(t1s) > 0 :
                    t1l = t1
                    t1  = t1s.pop(0)
                if abs(t2-t1) < abs(t2-t1l) :
                    skews.append(t2-t1)
                else :    
                    skews.append(t2-t1l)
        return skews
    #=========================================================================
    # METHOD: low_pass_pars
    # PURPOSE: dcgain, phase_margin, gain_margin, etc.
    #=========================================================================
    def low_pass_pars(self, frequency, signal, dcph_assumed=None) :
        """ low-pass response metrics: dcgain, phase_margin, gain_margin, etc.

        **arguments**:

            .. option:: frequency (int or str)

                column of frequency values of low-pass signal to characterize.
                If frequency is a string, it refers to the column named frequency.

            .. option:: signal (int or str)

                column of (complex) signal of low-pass signal to characterize.
                If signal is a string, it refers to the column named signal.
                REAL(signal) and IMAG(signal) must be present in data array.

            .. option:: dcph_assumed (float, default=None)

                specify phase of signal at DC.  If not specified, use value
                at lowest frequency.

        **results**:

            * Returns dictionary of low-pass metrics:

              * dcmag    : DC magnitude of signal

              * dcdb     : DC magnitude in dB (20*log10(magnitude)) of the signal

              * dcph     : DC phase of the signal

              * f0db     : frequency where signal is 0dB (unity gain)

              * pm       : phase-margin of the signal

              * f180deg  : frequency where the phase is -180 degrees (if so)

              * gm       : gain-margin of the signal

              * gbw_dec  : gain-bandwidth of the signal based on the signal
                           value 1 decade below the 0dB frequency.

              * f3db     : 3dB bandwidth of the signal

              * gbw_3db  : gain-bandwidth of the signal using the DC gain
                           times the 3dB bandwidth

              * f1db     : 1dB bandwidth of the signal

              * gbw_1db  : gain-bandwidth of the signal using the DC gain
                           times the 1dB bandwidth

              * peakdb   : the peak of the signal in dB

              * fpeak    : frequency of the peak of the signal

              * rolloff  : rolloff of the signal in dB/decade

              * g125deg  : gain of the signal where the phase is -125 degrees.

              * f125deg  : frequency where the phase is -125 degrees.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> LPFpars = d.low_pass_pars("frequency", "V(9)")
            >>> for par in LPFpars :
            ...     print "%s = %s" % (par, LPFpars[par])

        """
        #----------------------------------------------------------------------
        # get index of frequency:
        #----------------------------------------------------------------------
        ifreq = self.index(frequency)
        #----------------------------------------------------------------------
        # magnitute, db, phase:
        #----------------------------------------------------------------------
        imag = self.index("MAG("  + signal + ")")
        idb  = self.index("DB("   + signal + ")")
        iph  = self.index("PH("   + signal + ")")
        if imag == None or idb == None or iph == None :
            self.warning("magnitude, dB or phase columns for signal " 
                + signal + " not present"
            )
            return(None)
        #----------------------------------------------------------------------
        # gain and phase at dc (first point)
        #----------------------------------------------------------------------
        dcmag = self.get_entry(0, imag)
        dcdb  = self.get_entry(0, idb)
        dcph  = self.get_entry(0, iph)
        dcdb_3db = dcdb - 3
        dcdb_1db = dcdb - 1
        dcdb_max = self.max(idb)
        dcdb_min = self.min(idb)
        if dcph_assumed == None :
            dm180 = dcph + 180
            dp180 = dcph - 180
            if   abs(dm180) < abs(dcph) :
                dcph = dm180
            elif abs(dp180) < abs(dcph) :
                dcph = dp180
        else :
            dcph  = dcph_assumed
        dcph_180 = dcph - 180
        dcph_max = self.max(iph)
        dcph_min = self.min(iph)
        #---------------------------------------------------------------------
        # find f(0dB), phase-margin
        #---------------------------------------------------------------------
        if   dcdb_max > 0  and dcdb_min > 0 :
            # no gain=0dB crossings found: gain always above 0dB
            f0db = 1e18
            p0db = 0
            pm   = -1000
        elif dcdb_max <= 0 and dcdb_min <= 0 :
            # no gain=0dB crossings found: gain always equal to or below 0dB
            f0db = 0
            p0db = 0
            pm   = 1000
        else :
            f0db = self.crossings(ifreq, idb, 0)[0]
            p0db = self.crossings(iph, ifreq, f0db)[0]
            pm   = p0db - dcph_180
        #----------------------------------------------------------------------
        # find gain-margin
        #----------------------------------------------------------------------
        if   dcph_max >= dcph_180 and dcph_min >= dcph_180 :
            # no phase=-180deg crossings found: phase always above or = -180deg
            f180deg = 1e18
            gm = 1000
        elif dcph_max < dcph_180 and dcph_min < dcph_180 :
            # no phase=-180deg crossings were found: phase always below -180deg
            f180deg = 0
            gm      = -1000
        else :
            f180deg = self.crossings(ifreq, iph, dcph_180)[0]
            g180deg = self.crossings(idb, ifreq, f180deg)[0]
            gm      = -g180deg
        #-------------------------------------------------------------------
        # find freq, gain at phase = -125deg
        #-------------------------------------------------------------------
        zlist = self.crossings(ifreq, iph, dcph-125)
        if len(zlist) > 0 :
            f125deg = zlist[0]
            g125deg = self.crossings(idb, ifreq, f125deg)[0]
        else :
            f125deg = 0
            g125deg = -1000
        #-------------------------------------------------------------------
        # find -3dB point, gain/bandwidth using 3dB point
        #-------------------------------------------------------------------
        if dcdb_max > dcdb_3db and dcdb_min > dcdb_3db :
            # no gain=-3dB crossings were found: gain always above -3dB
            f3db    =  1e18
            gbw_3db =  1e18
        else :
            f3db    = self.crossings(ifreq, idb, dcdb_3db)[0]
            gbw_3db = dcmag*f3db
        #-------------------------------------------------------------------
        # find -1dB point, gain/bandwidth using 1dB point
        #-------------------------------------------------------------------
        if dcdb_max > dcdb_1db and dcdb_min > dcdb_1db :
            # no gain=-1dB crossings were found: gain always above -1dB
            f1db    = 1e18
            gbw_1db = 1e18
        else :
            f1db    = self.crossings(ifreq, idb, dcdb_1db)[0]
            gbw_1db = dcmag*f1db
        #-------------------------------------------------------------------
        # find bandwidth based on frequency 1 decade below 0dB point
        #-------------------------------------------------------------------
        fdec  = f0db*0.1
        zlist = self.crossings(idb, ifreq, fdec)
        if len(zlist) == 0 :
            gbw_dec = 0
        else :
            gain_dec = zlist[0]
            gbw_dec  = gain_dec*fdec
        #-------------------------------------------------------------------
        # peaking and rolloff
        #-------------------------------------------------------------------
        dpeak = self.dup()
        dpeak.filter("%s < %g" % (frequency, f3db))
        if dpeak.nrows() > 1 :
            peakdb = dpeak.max(idb)
            fpeak  = self.crossings(ifreq, idb, peakdb)[0]
            dpeak.set_parsed("logfreq = log10 %s" % (frequency))
            dpeak.set_parsed("slope   = DB(%s) dY/dX logfreq" % (signal))
            rolloff =  dpeak.get_entry(-1, "slope")
        else :
            peakdb  = 0
            fpeak   = 0
            rolloff = 0
        del(dpeak)
        #-------------------------------------------------------------------
        # return results:
        #-------------------------------------------------------------------
        R = {}
        pars = string.split("""
            dcmag dcdb dcph
            f0db pm f180deg gm
            gbw_dec f3db gbw_3db f1db gbw_1db
            peakdb fpeak rolloff
            f125deg g125deg
        """)
        for par in pars :
            R[par] = eval(par)
        return(R)
    #=========================================================================
    # METHOD: a2d
    # PURPOSE: convert bus of digital signals to bus value
    #=========================================================================
    def a2d(self, col, colspec, slice) :
        """ convert bus of digital signals to decimal values.

        **arguments**:

            .. option::  col (int or str)

                the column to place analog to digital values.
                If col is a string, it refers to the column named col.

            .. option:: col_spec (str)

                bus specification for columns to convert.
                The specification is bus<msb:lsb>, where bus is
                the bus name, msb is the most-sigificant bit
                and lsb is the least-significant bit.
                All bits of the bus must be present in the data set.
                For example, for bus<1:0>, the columns bus<1> and bus<0>
                must be present.

            .. option:: slice (float)

                value to slice the column data into digital values.
                if data > slice, digital value = 1, else 0.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.a2d("bus_a2d", "bus<3:0>", slice=0.5)

        """
        m = re.search("^([^<]+)<([0-9]+):([0-9]+)>(.*)$", colspec)
        if m:
            prefix  = m.group(1)
            bhi     = int(m.group(2))
            blo     = int(m.group(3))
            postfix = m.group(4)
            if bhi < blo :
                bhi, blo = blo, bhi
            buscols = []
            for i in range(blo, bhi+1) :
                bcol = prefix + "<" + str(i) + ">" + postfix
                if not bcol in self.names():
                    self.fatal("bus column \"%s\" not found in data" % (bcol))
                buscols.append(bcol)
            buscols.reverse()
        else :
            buscols = string.split(colspec)
            for bcol in buscols :
                if not bcol in self.names():
                    self.fatal("bus column \"%s\" not found in data" % (bcol))
        self.set("%s = 0" % (col))
        for bcol in buscols :
            self.set("%s = (2*%s) + (%s > %g)"  % (col, col, bcol, slice))
    #=========================================================================
    # METHOD: time_average
    # PURPOSE: measure time average of a column
    #=========================================================================
    def time_average(self, time, col) :
        """ measure time average of a column.

        **arguments**:

            .. option::  time (int or str)
       
                the column corresponding to time in the data array.
                If time is a string, it refers to the column named time.

            .. option::  col (int or str)

                the column corresponding to the signal in the data array
                to measure time average.
                If col is a string, it refers to the column named col.

        **results**:

            * The time average of col vs time is calculated as the integrated
              col divided by the time interval.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> tavg = d.time_average("time", "ivout")

        """
        t1 = self.get_entry( 0, time)
        t2 = self.get_entry(-1, time)
        sinteg = self.unique_name("integ")
        self.set_parsed("%s = %s integ %s" % (sinteg, col, time))
        self.set_parsed("%s = %s / %g"     % (sinteg, sinteg, t2-t1))
        time_average = self.get_entry(-1, sinteg)
        self.delete(sinteg)
        return(time_average)
    #=========================================================================
    # METHOD: period_time_average
    # PURPOSE: measure time average of a column within each cycle of time
    #=========================================================================
    def period_time_average(self, time, col,
        trigger=None, level=0, edge="rising",
        period=0, offset=0
    ) :
        """ measure time average of a column within each cycle of time.

        **arguments**:

            .. option::  time (int or str)
       
                the column corresponding to time in the data array.
                If time is a string, it refers to the column named time.

            .. option::  col (int or str)

                the column corresponding to the signal in the data array
                to measure time average.
                If col is a string, it refers to the column named col.

            .. option::  trigger (int or str) (optional default=None)

                the column corresponding to the signal in the data array
                to split up time into cycles of time.
                If trigger is a string, it refers to the column named trigger.
                If not specified, then the offset and period options are
                used to split up time into cycles of time.

            .. option::  level (float) (optional default=0.0)

                the level crossing of the trigger column to use to split
                up time into cycles of time.

            .. option::  edge (str) (optional default="rising")

                the edge crossing of the trigger column to use to split
                up time into cycles of time (using Data.crossings).
                one of ("rising", "falling", or "both").

            .. option::  period (float) (optional default=0.0)

                if trigger is not specified, the time period for splitting
                up time into cycles of time.

            .. option:: offset (float) (optional default=0.0)

                if trigger is not specified, the time offset for splitting
                up time into cycles of time.

        **results**:

            * The time axis is split up into cycles of time either by
              specifying a trigger column or by using period and offset.

            * Time averages are computed for each cycle of time.

            * A data object is returned with time and time-average columns.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> tavg = d.period_time_average("time", "ivout", trigger="zout")

        """
        arrt = self.get(time)
        arrs = self.get(col)
        if trigger is not None:
            times = self.crossings(time, trigger, level=level, edge=edge)
        elif period > 0 :
            times = decida.range_sample(offset, self.max(time), step=period)
        else :
            return
        rows = arrt.searchsorted(times)
        mids = []
        avgs = []
        for i1, i2 in zip(rows[:-1], rows[1:]) :
            t1 = arrt[i1]
            t2 = arrt[i2-1]
            per = (t2 - t1)
            mid = (t2 + t1)*0.5
            avg = numpy.trapz(arrs[i1:i2], x=arrt[i1:i2])
            mids.append(mid)
            avgs.append(avg/per)
        d = Data()
        d.read_inline("time", mids, "avg", avgs)
        return d
    #=========================================================================
    # METHOD: rms
    # PURPOSE: measure RMS value of a column
    #=========================================================================
    def rms(self, time, col) :
        """ measure RMS value of a column.

        **arguments**:

            .. option::  time (int or str)
       
                the column corresponding to time in the data array.
                If time is a string, it refers to the column named time.

            .. option::  col (int or str)

                the column corresponding to the signal in the data array
                to measure RMS value.
                If col is a string, it refers to the column named col.

        **results**:

            * The RMS value of col vs time is calculated as the 
              square-root of the integrated
              squared(col) divided by the time interval.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> tavg = d.rms("time", "ivout")

        """
        t1 = self.get_entry( 0, time)
        t2 = self.get_entry(-1, time)
        sinteg = self.unique_name("integ")
        if False:
            self.set_parsed("%s = %s * %s"     % (sinteg, col, col))
            self.set_parsed("%s = %s integ %s" % (sinteg, sinteg, time))
            self.set_parsed("%s = %s / %g"     % (sinteg, sinteg, t2-t1))
            self.set_parsed("%s = sqrt %s"     % (sinteg, sinteg))
        else :
            self.set("%s = sqrt(integ(%s*%s,%s)/%g)" % \
                 (sinteg, col, col, time, t2-t1))
        rms = self.get_entry(-1, sinteg)
        self.delete(sinteg)
        return(rms)
    #=========================================================================
    # METHOD: lpf
    # PURPOSE: low-pass filter
    #=========================================================================
    def lpf(self, filter_col, signal, time, fpole) :
        """ low-pass filter.

        **arguments**:

            .. option:: filter_col (str)

                output filter column.

            .. option:: signal (int or str)

                input signal column.
                If signal is a string, it refers to the column named signal.

            .. option:: time (int or str)

                input time column.
                If time is a string, it refers to the column named time.

            .. option:: fpole (float)

                the low-pass filter pole.
 
        **results**:

            * Calculate low-pass filtered data values.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.lpf("y_filtered", "y", "time", fpole=1e8)

        """
        pi   = math.acos(-1)
        #---------------------------------------------------------------------
        # check to see if time and signal are columns
        #---------------------------------------------------------------------
        if not time in self.names() :
            self.error("time \"%s\" is not in data" % (time))
            return
        if not signal in self.names() :
            self.error("signal \"%s\" is not in data" % (signal))
            return
        #---------------------------------------------------------------------
        # check to see if pole is within range
        #---------------------------------------------------------------------
        tdel = self.unique_name("tmp")
        self.append(tdel)
        self.set("%s = del(%s)" % (tdel, time))
        tdelmin = self.min(tdel)
        if tdelmin <= 0.0:
            self.error("%s is not strictly ascending" % (time),
                "min(delta(%s)) = %g" % (time, tdelmin))
            self.delete(tdel)
            return
        if fpole <= 0.0 or fpole >= 0.5/tdelmin :
            self.error("pole %g is out of range" % (fpole),
                "must be > 0 and < %g" % (0.5/tdelmin))
            self.delete(tdel)
            return
        #---------------------------------------------------------------------
        # perform filtering
        #---------------------------------------------------------------------
        y = self.get_entry(0, signal)
        z = y
        self.set_parsed("%s = 0.0" % (filter_col))
        self.set_entry(0, filter_col, z)
        n = self.nrows()
        for i in range(1, n) :
            yl = y
            y  = self.get_entry(i, signal)
            xd = self.get_entry(i, tdel)
            ya = (y + yl)*0.5
            a  = math.tan(pi+fpole*xd)
            a  = 2/(1 + 1/a)
            z  = z + a*(ya-z)
            self.set_entry(i, filter_col, z)
        self.delete(tdel)
    #=========================================================================
    # METHOD  : moving_average_filter
    # PURPOSE : moving-average filter
    #=========================================================================
    def moving_average_filter(self, filter_col, signal, navg=21) :
        """ moving-average filter.

        **arguments**:

            .. option:: filter_col (int or str)

                output filtered column.
                If filter_col is a string, it refers to the column
                named filter_col.

            .. option:: signal (int or str)

                input signal column to filter.
                If signal is a string, it refers to the column
                named signal.

            .. option:: navg (int, default=21)

                number of points in the averaging window.

        **results**:

            * number of points in the averaging window must be odd, so if
              navg is specified as an even number, the averaging window is
              increased by 1.

            * does not check to see if navg is greater than the number of
              rows in the data array, or if it is specified as < 1.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.moving_average("in_filter", "in", navg=21)

        """
        #---------------------------------------------------------------------
        # check to see if signal is column
        #---------------------------------------------------------------------
        if not signal in self.names() :
            self.error("signal \"%s\" is not in data" % (signal))
            return
        #---------------------------------------------------------------------
        # midpoint value
        #---------------------------------------------------------------------
        npts = self.nrows()
        if navg % 2 == 0:
            navg += 1
        m = (navg-1) / 2
        #---------------------------------------------------------------------
        # find average of first navg points
        #---------------------------------------------------------------------
        self.set("%s = 0.0" % (filter_col))
        acc = 0.0
        for i in range(0, navg) :
            acc += self.get_entry(i, signal)
        self.set_entry(m, filter_col, acc/navg)
        #---------------------------------------------------------------------
        # recursively find average of following points
        #---------------------------------------------------------------------
        for i in range(m+1, npts-m) :
            acc -= self.get_entry(i-(m+1), signal)
            acc += self.get_entry(i+(m),   signal)
            self.set_entry(i, filter_col, acc/navg)
    #=========================================================================
    # METHOD  : edges
    # PURPOSE : find edge metrics
    #=========================================================================
    def edges(self, xcol, ycol, vlow=None, vhigh=None) :
        """ find edge metrics.

        **arguments**:

            .. option:: xcol (int or str)

                time column.
                If xcol is a string, it refers to the column named xcol.

            .. option:: ycol (int or str)

                signal column to measure edges.
                If ycol is a string, it refers to the column named ycol.

            .. option:: vlow (float, default=None)

                low signal value for calculating edges.
                If vlow is None, use min(ycol).

            .. option:: vhigh (float, default=None)

                high signal value for calculating edges.
                If vhigh is None, use max(ycol).

        **results**:

            * calculate all of the following rise time and fall time
              metrics:

                   * rise_time_10_90 : rising edge time 10% to 90%

                   * rise_time_20_80 : rising edge time 20% to 80%

                   * rise_time_30_70 : rising edge time 30% to 70%

                   * rise_time_40_60 : rising edge time 40% to 60%

                   * fall_time_10_90 : falling edge time 90% to 10%

                   * fall_time_20_80 : falling edge time 80% to 20%

                   * fall_time_30_70 : falling edge time 70% to 30%

                   * fall_time_40_60 : falling edge time 60% to 40%

                   * rise_slew_10_90 : rising edge slew 10% to 90%

                   * rise_slew_20_80 : rising edge slew 20% to 80%

                   * rise_slew_30_70 : rising edge slew 30% to 70%

                   * rise_slew_40_60 : rising edge slew 40% to 60%

                   * fall_slew_10_90 : riseing edge slew 90% to 10%

                   * fall_slew_20_80 : falling edge slew 80% to 20%

                   * fall_slew_30_70 : falling edge slew 70% to 30%

                   * fall_slew_40_60 : falling edge slew 60% to 40%

            * return a new Data object with the edge metrics for each edge.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d1 = d.edges("time", "v(z)", vlow=0.0, vhigh=1.2)

        """
        #---------------------------------------------------------------------
        # check to see if xcol and ycol are columns
        #---------------------------------------------------------------------
        if not xcol in self.names() :
            self.warning("x-column \"%s\" is not in data" % (xcol))
            return
        if not ycol in self.names() :
            self.warning("y-column \"%s\" is not in data" % (ycol))
            return
        #---------------------------------------------------------------------
        # if low and/or high are None, figure out limits
        #---------------------------------------------------------------------
        if vlow is None :
            vlow = self.min(ycol)
        if vhigh is None :
            vhigh = self.max(ycol)
        #---------------------------------------------------------------------
        # find rising edge and falling edge statistics
        #---------------------------------------------------------------------
        Rise = {}
        Fall = {}
        dv = vhigh - vlow
        tr = 0
        tf = 0
        start = True
        for pctr in range(10, 100, 10) :
            pctf = 100 - pctr
            vxr = vlow + dv*0.01*pctr
            vxf = vlow + dv*0.01*pctf
            Rise[pctr] = self.crossings(xcol, ycol, vxr, edge="rising")
            Fall[pctf] = self.crossings(xcol, ycol, vxf, edge="falling")
            if len(Rise[pctr]) > 0 and Rise[pctr][0] < tr :
                Rise[pctr].pop(0)
            if len(Fall[pctf]) > 0 and Fall[pctf][0] < tf :
                Fall[pctf].pop(0)
            if len(Rise[pctr]) > 0 :
                tr = Rise[pctr][0]
            if len(Fall[pctf]) > 0 :
                tf = Fall[pctf][0]
            if start :
                leng = len(Rise[pctr])
                start = False
            leng = min(leng, len(Rise[pctr]), len(Fall[pctf]))
        #---------------------------------------------------------------------
        # 0 length case
        #---------------------------------------------------------------------
        if leng == 0 :
            self.warning("equalized lists of rise and fall times are empty")
            if len(Rise[10]) > 0 and len(Rise[90]) > 0 :
               print "10% to 90% rise times:"
               for tr10, tr90 in zip(Rise[10], Rise[90]) :
                   print tr90 - tr10
            if len(Rise[20]) > 0 and len(Rise[80]) > 0 :
               print "20% to 80% rise times:"
               for tr20, tr80 in zip(Rise[20], Rise[80]) :
                   print tr80 - tr20
            if len(Rise[30]) > 0 and len(Rise[70]) > 0 :
               print "30% to 70% rise times:"
               for tr30, tr70 in zip(Rise[30], Rise[70]) :
                   print tr70 - tr30
            if len(Fall[10]) > 0 and len(Fall[90]) > 0 :
               print "90% to 10% fall times:"
               for tf10, tf90 in zip(Fall[10], Fall[90]) :
                   print tf90 - tf10
            if len(Fall[20]) > 0 and len(Fall[80]) > 0 :
               print "80% to 20% fall times:"
               for tf20, tf80 in zip(Fall[20], Fall[80]) :
                   print tf80 - tf20
            if len(Fall[30]) > 0 and len(Fall[70]) > 0 :
               print "70% to 30% fall times:"
               for tf30, tf70 in zip(Fall[30], Fall[70]) :
                   print tf70 - tf30
            return
        #---------------------------------------------------------------------
        # trim lists to be same length
        #---------------------------------------------------------------------
        for pct in range(10, 100, 10) :
            Rise[pct]=Rise[pct][0:leng]
            Fall[pct]=Fall[pct][0:leng]
        #---------------------------------------------------------------------
        # new data object with lists of edges
        #---------------------------------------------------------------------
        d1 = Data()
        d1.read_inline(
           "rise_10pct", Rise[10], "fall_10pct", Fall[10],
           "rise_20pct", Rise[20], "fall_20pct", Fall[20],
           "rise_30pct", Rise[30], "fall_30pct", Fall[30],
           "rise_40pct", Rise[40], "fall_40pct", Fall[40],
           "rise_50pct", Rise[50], "fall_50pct", Fall[50],
           "rise_60pct", Rise[60], "fall_60pct", Fall[60],
           "rise_70pct", Rise[70], "fall_70pct", Fall[70],
           "rise_80pct", Rise[80], "fall_80pct", Fall[80],
           "rise_90pct", Rise[90], "fall_90pct", Fall[90]
        )
        delcols = d1.names()
        #---------------------------------------------------------------------
        # calculate rise/fall time rise/fall slew metrics
        #---------------------------------------------------------------------
        for pct in range(10, 50, 10) :
            pto = 100 - pct
            dvp = dv*0.01*(pto-pct) 
            d1.set("rise_time_%d_%d = rise_%dpct - rise_%dpct" % \
                (pct, pto, pto, pct))
            d1.set("fall_time_%d_%d = fall_%dpct - fall_%dpct" % \
                (pct, pto, pct, pto))
            d1.set("rise_slew_%d_%d = %e / rise_time_%d_%d" % \
                (pct, pto, dvp, pct, pto))
            d1.set("fall_slew_%d_%d = %e / fall_time_%d_%d" % \
                (pct, pto, dvp, pct, pto))
        d1.insert(-1, "point")
        d1.set_parsed("point = index")
        d1.delete(delcols)
        return d1
    #=========================================================================
    # METHOD: is_equally_spaced
    # PURPOSE: examines data column to see if it is equally-spaced
    #=========================================================================
    def is_equally_spaced(self, col, threshold=1e-15) :
        """ examines data column to see if it is equally-spaced.

        **arguments**:

            .. option:: col (int or str)

                the column in the data array. If col is a string, it refers
                to the column named col

            .. option:: threshold (float, default=1e-15)

                maximum value that values can be different before considering
                them as unequally-spaced.

        **results**:

            * If values are unequally-spaced, return False, else True.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.is_equally_spaced("time")

        """
        tmp=self.unique_name("tmp")
        self.set("%s = abs(del(del(%s))) > %g" % (tmp, col, threshold))
        values = self.unique("%s" % (tmp))
        self.delete(tmp)
        if len(values) == 1 and values[0] == 0:
           return True
        return False
    #=========================================================================
    # METHOD: reverse
    # PURPOSE: reverse order of data in a column
    #=========================================================================
    def __reverse(self, *args) :
        """ reverse. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: col_scrub
    # PURPOSE: scrub column of NaN's
    #=========================================================================
    def __col_scrub(self, *args) :
        """ col_scrub. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: crosspoints
    # PURPOSE: crosspoints
    #=========================================================================
    def __crosspoints(self, *args) :
        """ crosspoints. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: eye_loc
    # PURPOSE: eye_loc
    #=========================================================================
    def __eye_loc(self, *args) :
        """ eye_loc. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: find_rows
    # PURPOSE: find_rows
    #=========================================================================
    def __find_rows(self, *args) :
        """ find_rows. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: measure_delay
    # PURPOSE: measure_delay
    #=========================================================================
    def __measure_delay(self, *args) :
        """ measure_delay. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: measure_freq
    # PURPOSE: measure_freq
    #=========================================================================
    def measure_freq(self, xcol, ycol, level=None, edge="rising") :
        """ measure frequency of a signal column.

        **arguments**:

            .. option:: xcol (int or str)

                time column.
                If xcol is a string, it refers to the column named xcol.

            .. option:: ycol (int or str)

                signal column.
                If ycol is a string, it refers to the column named ycol.

            .. option::  level (float, default=None)

                signal crossing level to use.  If level is None, use
                0.5*(max(ycol) + min(ycol))

            .. option::  edge (str, default="both")

                signal edge(s) to use to accumulate crossings.
                values must be in ("rising", "falling")

        **results**:

            * Returns the frequency of the last few signal crossings.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> freq = d.measure_freq("time", "v(out)", level=0.4)

        """
        if not xcol in self.names() :
            self.warning("x-column \"%s\" is not in data" % (xcol))
            return(0)
        if not ycol in self.names() :
            self.warning("y-column \"%s\" is not in data" % (ycol))
            return(0)
        if level == None :
            ymax = self.max(ycol)
            ymin = self.min(ycol)
            level = 0.5*(ymax+ymin)
        crossings = self.crossings(
            xcol=xcol, ycol=ycol, level=level, edge=edge)
        if len(crossings) >= 4:
            period = (crossings[-1] - crossings[-3]) / 2.0
        elif len(crossings) == 3:
            period = (crossings[-1] - crossings[-2])
        elif len(crossings) == 2:
            period = (crossings[-1] - crossings[-2])
        else :
            period = 1e8
            self.warning("not enough crossings to determine frequency")
        frequency  = 1.0/period
        return(frequency)
    #=========================================================================
    # METHOD: measure_duty
    # PURPOSE: measure_duty
    #=========================================================================
    def measure_duty(self, xcol, ycol, level=None) :
        """ measure duty-cycle of a signal column.

        **arguments**:

            .. option:: xcol (int or str)

                time column.
                If xcol is a string, it refers to the column named xcol.

            .. option:: ycol (int or str)

                signal column.
                If ycol is a string, it refers to the column named ycol.

            .. option::  level (float, default=None)

                signal crossing level to use.  If level is None, use
                0.5*(max(ycol) + min(ycol))

        **results**:

            * Returns the duty-cycle of the last few signal crossings.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> freq = d.measure_duty("time", "v(out)", level=0.4)

        """
        if not xcol in self.names() :
            self.warning("x-column \"%s\" is not in data" % (xcol))
            return(0)
        if not ycol in self.names() :
            self.warning("y-column \"%s\" is not in data" % (ycol))
            return(0)
        if level == None :
            ymax = self.max(ycol)
            ymin = self.min(ycol)
            level = 0.5*(ymax+ymin)
        crossings = self.crossings(
            xcol=xcol, ycol=ycol, level=level, edge="transitions")
        if len(crossings) >= 3:
            t1, e1 = crossings[-3]
            t2, e2 = crossings[-2]
            t3, e3 = crossings[-1]
            period = t3 - t1
            if period > 0.0 :
                if e2 == 1 :
                    duty_cycle = 100.0*(t3-t2)/period
                else :
                    duty_cycle = 100.0*(t2-t1)/period
            else :
                self.warning("period is not > 0")
        else :
            duty_cycle = 0.0
            self.warning("not enough crossings to determine duty_cycle")
        return(duty_cycle)
    #=========================================================================
    # METHOD: measure_slew
    # PURPOSE: measure_slew
    #=========================================================================
    def __measure_slew(self, *args) :
        """ measure_slew. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: fft
    # PURPOSE: FFT
    #=========================================================================
    def fft(self, zcol, ycol, xcol, window="hamming") :
        """ fast-fourier transform (FFT).

        **arguments**:

            .. option:: zcol (str)

                FFT complex variable name to create.

            .. option:: ycol (int or str)

                input signal column to transform.
                If ycol is a string, it refers to the column named ycol.

            .. option:: xcol (int or str)

                input time column for FFT.
                If xcol is a string, it refers to the column named xcol.

            .. option:: window (str, default="hamming")

                FFT windowing type.  Must be one of: 
                "bartlett", "blackman", "hamming", or "hanning"

        **results**:

            * xcol and ycol values are linearly interpolated on an equally-spaced
              set of 2^power values, where 2^power is the next power of 2 greater
              than the number of rows in the data array.

            * the ycol interpolated values are windowed using the specified
              windowing function.

            * frequency and FFT values are created and entered into a new 
              Data object, which is returned.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> dfft = d.fft("zcol", "v(out)","time", window="hamming")

        """
        #---------------------------------------------------------------------
        # check to see if xcol and ycol are columns
        #---------------------------------------------------------------------
        if not xcol in self.names() :
            self.warning("x-column \"%s\" is not in data" % (xcol))
            return
        if not ycol in self.names() :
            self.warning("y-column \"%s\" is not in data" % (ycol))
            return
        windows = ("bartlett", "blackman", "hamming", "hanning")
        if not window in windows :
            self.warning("window must be one of %s" % (windows))
        #---------------------------------------------------------------------
        # map onto uniform grid of 2^x points
        #---------------------------------------------------------------------
        x0 = self.get_entry(0, xcol)
        xn = self.get_entry(-1, xcol)
        nr = self.nrows()
        np = int(math.pow(2.0, int(math.log(nr)/math.log(2) + 0.5)))
        if np < nr :
            np *= 2
        xdata = decida.range_sample(x0, xn, num=np)
        #---------------------------------------------------------------------
        # frequency data
        #---------------------------------------------------------------------
        fdata = []
        fd = 1/(xn-x0)
        for i in range(0, (np/2 + 1)) :
            fdata.append(i*fd)
        #---------------------------------------------------------------------
        # interpolate ydata onto uniform grid
        #---------------------------------------------------------------------
        ydata = []
        n = 0
        for x in xdata :
            found = False
            while n < nr - 1 :
                xp = self.get_entry(n, xcol)
                if xp >= x:
                    found = True
                    break
                n += 1
            yp = self.get_entry(n, ycol)
            if found and n > 0 :
                xm = self.get_entry(n-1, xcol)
                ym = self.get_entry(n-1, ycol)
                yp = ym + (yp-ym)*(x-xm)/(xp-xm)
            ydata.append(yp)
        #---------------------------------------------------------------------
        # apply window
        #---------------------------------------------------------------------
        fwindow = {
            "bartlett" : numpy.bartlett,
            "blackman" : numpy.blackman,
            "hamming"  : numpy.hamming,
            "hanning"  : numpy.hanning,
        }[window]
        ydata = numpy.multiply(fwindow(np), ydata)
        if False :
            dx=Data()
            dx.read_inline("xdata", xdata, "ydata", ydata)
            dx.write_ssv("%s.col" % (window))
            del dx 
        #---------------------------------------------------------------------
        # FFT
        #---------------------------------------------------------------------
        zdata  = numpy.fft.rfft(ydata)
        zrdata = numpy.real(zdata)
        zidata = numpy.imag(zdata)
        d=Data()
        d.read_inline(
            "frequency", fdata,
            "REAL(%s)" % (zcol), zrdata,
            "IMAG(%s)" % (zcol), zidata
        )
        d.cxmag(zcol)
        return d
    #=========================================================================
    # METHOD: eye_time
    # PURPOSE: create eye_diagram time column
    #=========================================================================
    def eye_time(self, time, eyetime, period, offset=0.0) :
        """ create eye_diagram time column.

        **arguments**:

        .. option:: time (str or int)

            time column

        .. option:: eyetime (str)

            eye_time column to generate or overwrite

        .. option:: period (float)

            eye-diagram period

        .. option:: offset (float, default=0.0)

            eye-diagram time offset

        **example**:

            >>> from decida.Data import Data
            >>> from decida.XYplotx import XYplotx
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.eye_time("time", "eye_time", 10e-9, 0.0)
            >>> XYplotx(command=[d, "eye_time v(dout)"])

        """
        self.set_parsed("%s = 0.0" % (eyetime))
        if period <= 0.0 :
            self.warning("period must be > 0")
            return
        z = offset
        for i, t in enumerate(self.get(time)) :
            while t < (z - period) :
                z -= period
            while t >= z :
                z += period
            self.set_entry(i, eyetime, t - (z-period))
    #=========================================================================
    # METHOD: osc_time
    # PURPOSE: create oscilloscope time column
    #=========================================================================
    def osc_time(self, time, osctime, trigger, period, level=None,
        edge="rising"
    ) :
        """ create oscilloscope time column.

        **arguments**:

        .. option:: time (str or int)

            time column

        .. option:: osctime (str)

            osc_time column to generate or overwrite

        .. option:: trigger (str or int)

            trigger column.

        .. option:: period (float)

            time period 

        .. option:: level (float, default = None)

            trigger level. If not specified, 
            level = 0.5*(max(trigger) - min(trigger))

        .. option:: edge (str, default="rising")

            edge of trigger column to use to trigger the osc_time sweep.
            must be one of  "rising", "falling", or "both"

        **example**:

            >>> from decida.Data import Data
            >>> from decida.XYplotx import XYplotx
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.osc_time("time", "osc_time", "clock", 10e-9, 0.5, "rising")
            >>> XYplotx(command=[d, "osc_time v(dout)"])

        """
        self.set_parsed("%s = 0.0" % (osctime))
        if not level :
            level = 0.5*(self.min(trigger) + self.max(trigger))
        rising  = (edge == "rising"  or edge == "both")
        falling = (edge == "falling" or edge == "both")
        triggered = False
        start = True
        for i, t in enumerate(self.get(time)) :
            s = self.get_entry(i, trigger)
            if start :
                to = 0.0
                start = False
            elif not triggered :
                to = 0.0
                rp = (s >= level) and (s_p < level)
                fp = (s <= level) and (s_p > level)
                if (rising and rp) or (falling and fp) :
                    tx = t_p + (level-s_p)*(t-t_p)/(s-s_p)
                    to = t - tx
                    triggered = True
            else :
                to = t - tx
                if to > period :
                    to = 0.0
                    triggered = False
            self.set_entry(i, osctime, to)
            t_p, s_p = t, s
    #=========================================================================
    # METHOD: pzview
    # PURPOSE: pole-zero view
    #=========================================================================
    def __pzview(self, *args) :
        """ pole-zero view. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: transpose
    # PURPOSE: transpose data array
    #=========================================================================
    def __transpose(self, *args) :
        """ transpose data array. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: jitter
    # PURPOSE: measure jitter of clock waveform
    #=========================================================================
    def jitter(self, time, signal, tmin=None, tmax=None, freq=None,
        level=None, nbins=21, prefix="jitter", edge="rising", clock=True,
        prt=True, plot=False
    ) :
        """ measure jitter metrics of clock waveform.

        **arguments**:

            .. option:: time (int or str)

                time column.
                If time is a string, it refers to the column named time.

            .. option:: signal (int or str)

                clock signal column.
                If signal is a string, it refers to the column named signal.

            .. option:: tmin (float, default=None)

                minimum time to use to calculate jitter metrics.
                If tmin is not specified, use minimum time in the data array.

            .. option:: tmax (float, default=None)

                maximum time to use to calculate jitter metrics.
                If tmax is not specified, use maximum time in the data array.

            .. option:: freq (float, default=None)

                frequency of the reference clock to compare with the 
                clock signal.  If not specified, use the average frequency
                of the signal.

            .. option:: level (float, default=None)

                level to use for level crossings of the signal.  If not specified,
                use 0.5*(max(signal) + min(signal))

            .. option:: nbins (int, default=21)

                number of bins for histogram calculations of the jitter.

            .. option:: prefix (str, default="jitter")

                prefix of files for storing calculated jitter data.

            .. option:: edge (str, default="rising")

                edge of signal to use for level crossings.  Must be one of
                "rising", "falling" or "both"

            .. option:: clock (bool, default=True)

                if clock=True, signal is assumed to be a clock signal, and
                jitter is calculated with respect to the same crossing as the
                reference clock.  If clock=False, signal is assumed to be
                a data signal, and jitter is calculated with respect to the
                closest reference clock edge.

            .. option:: prt (bool, default=True)

                if True, print out report text

            .. option:: plot (bool, default=False)

                if True, generate a plot of the jitter metrics. (TBD)

        **results**:

            * Calculates absolute jitter, period jitter and cycle-to cycle jitter.

               * absolute jitter values are the difference between the signal
                 level crossings and the crossings of the reference clock.

               * period jitter values are the difference between adjacent 
                 signal jitter values.

               * cycle-to-cycle jitter values are the differences between
                 adjacent signal periods.

            * Returns dictionary of statistics of the different jitter metrics,
              and jitter analysis report.
            
                * Ja_pp  : peak-to-peak of the absolute jitter values
                * Jp_pp  : peak-to-peak of the period jitter values
                * Jc_pp  : peak-to-peak of the cycle-to-cycle jitter values
                * Ja_rms : RMS of the absolute       jitter values
                * Jp_rms : RMS of the period         jitter values
                * Jc_rms : RMS of the cycle-to-cycle jitter values
                * report : jitter report

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.jitter("time", "vout")

        """
        #---------------------------------------------------------------------
        # error if time or signal columns aren't present
        #---------------------------------------------------------------------
        if not time in self.names() :
            self.warning("time column \"%s\" isn't present" % (time))
            return
        if not signal in self.names() :
            self.warning("signal column \"%s\" isn't present" % (signal))
            return
        #-------------------------------------------------------------------
        # if time limits weren't specified, use min and max of time column
        #-------------------------------------------------------------------
        if tmin is None :
            tmin = self.min(time)
        if tmax is None :
            tmax = self.max(time)
        #-------------------------------------------------------------------
        # if level wasn't specified, use 1/2*(min + max)
        # time column
        #-------------------------------------------------------------------
        vmin = self.min(signal)
        vmax = self.max(signal)
        vavg = self.mean(signal)
        if level is None :
            level = (vmin + vmax)*0.5
        #-------------------------------------------------------------------
        # if data signal:
        #   use both edges
        #   error if freq not specified
        #-------------------------------------------------------------------
        if not clock :
            edge = "both"
            if freq is None :
                self.warning("for data signal, must specify frequency")
                return
        #-------------------------------------------------------------------
        # crossings, trim off t<tmin t>tmax crossings
        #-------------------------------------------------------------------
        Vreturn = {
            "Ja_pp" : 0.0, "Jp_pp" : 0.0, "Jc_pp" : 0.0,
            "Ja_rms": 0.0, "Jp_rms": 0.0, "Jc_rms": 0.0,
        }
        ts = self.crossings(time, signal, level=level, edge=edge)
        tx = []
        for t in ts :
            if t >= tmin and t <= tmax:
                tx.append(t)
        if len(tx) < 2 :
            self.warning("less than 2 signal crossings found")
            return Vreturn
        ncross = len(tx)
        #-------------------------------------------------------------------
        # calculate frequency, if not specified
        #-------------------------------------------------------------------
        t1 = tx.pop(0)
        t2 = tx[-1]
        if freq is None:
            rstep = (t2-t1)/len(tx)
            if edge == "both" :
                period = rstep*2.0
            else :
                period = rstep
            if period == 0.0 :
                self.warning("calculated period is 0")
                return Vreturn
            freq = 1.0/period
        else :
            if freq <= 0.0 :
                self.warning("specified frequency is <= 0")
                return Vreturn
            period = 1.0/freq
            if edge == "both" :
                rstep = period*0.5
            else :
                rstep = period
        #-------------------------------------------------------------------
        # calculate difference between ideal and signal crossings
        # J  is absolute jitter
        # P  is period
        # dJ is difference between adjacent jitters
        # dP is difference between adjacent periods
        #-------------------------------------------------------------------
        dj = Data()
        dj.append("tref", "t", "J", "P", "dJ", "dP")
        tm1 = t1
        jm1 = 0.0
        pm1 = 0.0
        tref = t1
        for t in tx:
            tref += rstep
            #-----------------------------------------------------------------
            # for a data signal, find the closest reference time and assume
            # that this is the respective crossing for calculating jitter.
            # This assumption may underestimate jitter in some cases.
            #-----------------------------------------------------------------
            if not clock:
                while t > tref+0.5*rstep :
                    tref += rstep
            #-----------------------------------------------------------------
            # calculate plotting data (TBD)
            #-----------------------------------------------------------------
            #-----------------------------------------------------------------
            # jitter metrics
            #-----------------------------------------------------------------
            J  = t - tref
            P  = t - tm1
            dJ = J - jm1
            dP = P - pm1
            tm1 = t
            jm1 = J
            pm1 = P
            dj.row_append()
            dj.set_entry(-1, "tref", tref)
            dj.set_entry(-1, "t", t)
            dj.set_entry(-1, "J", J)
            dj.set_entry(-1, "P", P)
            dj.set_entry(-1, "dJ", dJ)
            dj.set_entry(-1, "dP", dP)
        dj.set_parsed("point = index")
        dj.write_ssv("jitter.col")
        p_avg  = dj.mean("P")
        p_min  = dj.min("P")
        p_max  = dj.max("P")
        ja_avg = dj.mean("J")
        ja_rms = dj.std("J")
        ja_max = dj.max("J")
        ja_min = dj.min("J")
        ja_p_p = ja_max - ja_min
        jp_avg = dj.mean("dJ")
        jp_rms = dj.std("dJ")
        jp_max = dj.max("dJ")
        jp_min = dj.min("dJ")
        jp_p_p = jp_max - jp_min
        dj.filter("point > 0")
        jc_avg = dj.mean("dP")
        jc_rms = dj.std("dP")
        jc_max = dj.max("dP")
        jc_min = dj.min("dP")
        jc_p_p = jc_max - jc_min
        Vreturn = {
            "Ja_pp" : ja_p_p, "Jp_pp" : jp_p_p, "Jc_pp" : jc_p_p,
            "Ja_rms": ja_rms, "Jp_rms": jp_rms, "Jc_rms": jc_rms,
        }
        #-------------------------------------------------------------------
        # report
        #-------------------------------------------------------------------
        report = []
        report.append("#" + "=" * 72)
        report.append("# (%s) %s jitter" % (prefix, signal))
        report.append("#" + "=" * 72)
        report.append("time : %s" % (time))
        report.append("    minimum        : %-12.4g" % (tmin))
        report.append("    maximum        : %-12.4g" % (tmax))
        report.append("ideal clock :")
        report.append("    frequency      : %-12.4g MHz" % (freq*1e-6))
        report.append("    period         : %-12.4g ps"  % (period*1e12))
        report.append("signal : %s" % (signal))
        report.append("    average        : %-12.4g" % (vavg))
        report.append("    minimum        : %-12.4g" % (vmin))
        report.append("    maximum        : %-12.4g" % (vmax))
        report.append("    crossing level : %-12.4g" % (level))
        report.append("    no. crossings  : %-d" % (ncross))
        report.append("    period (mean)  : %-12.4g us" % (p_avg  * 1e6))
        report.append("    period (min)   : %-12.4g us" % (p_min  * 1e6))
        report.append("    period (max)   : %-12.4g us" % (p_max  * 1e6))
        report.append("    jitter (min)   : %-12.4g ps" % (ja_min * 1e12))
        report.append("    jitter (max)   : %-12.4g ps" % (ja_max * 1e12))
        report.append("    Jabs           : %-12.4g ps p-p / %-12.4g ps rms" % \
            (ja_p_p * 1e12, ja_rms * 1e12))
        report.append("    Jper           : %-12.4g ps p-p / %-12.4g ps rms" % \
            (jp_p_p * 1e12, jp_rms * 1e12))
        report.append("    Jc_c           : %-12.4g ps p-p / %-12.4g ps rms" % \
            (jc_p_p * 1e12, jc_rms * 1e12))
        report = string.join(report, "\n")
        #-------------------------------------------------------------------
        # return
        #-------------------------------------------------------------------
        if prt :
            print report
        Vreturn["report"] = report
        return Vreturn
    #=========================================================================
    # METHOD: tracking_jitter
    # PURPOSE: measure tracking jitter of two clock waveforms
    #=========================================================================
    def __tracking_jitter(self, *args) :
        """ measure tracking jitter of two clock waveforms. (not yet done)"""
        pass
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # complex
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #=========================================================================
    # METHOD: cxreim
    # PURPOSE: return real and imaginary column indices
    # NOTE: if create is true, make new columns
    #=========================================================================
    def cxreim(self, cxvar, create=False, nocomplain=False) :
        """ return real and imaginary column indices.

        **arguments**:

            .. option:: cxvar (str)

               complex variable name, represented by data array columns
               REAL(cxvar) and IMAG(cxvar)

            .. option::create (bool, default=False)

               if True, create new data columns REAL(cxvar) and IMAG(cxvar),
               if they do not already exist.

            .. option::nocomplain (bool, default=False)

               if True, don't complain if REAL(cxvar) or IMAG(cxvar)
               data columns are not present and create is False.

        **results**:

            * return real and imaginary columns for the complex variable
              cxvar (REAL(cxvar) and IMAG(cxvar).

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> re, im = d.cxreim("s11")
        """
        re="REAL(%s)" % (cxvar)
        im="IMAG(%s)" % (cxvar)
        ire=self.index(re)
        iim=self.index(im)
        if (ire == None) :
            if create :
                self.append(re)
                ire = self.index(re)
            elif not nocomplain:
                self.warning("real column for %s not found" % (cxvar))
        if (iim == None) :
            if create :
                self.append(im)
                iim = self.index(im)
            elif not nocomplain:
                self.warning("imag column for %s not found" % (cxvar))
        return((ire, iim))
    #=========================================================================
    # METHOD: cxset_parsed
    # PURPOSE: basic column operations on parsed equation (complex)
    #=========================================================================
    def cxset_parsed(self, equation) :
        """ basic column operations on parsed equation (complex).
        
        **arguments**:

            .. option:: equation (str)

                An equation which has been parsed into space-separated
                tokens. Data.cxset() uses Data.cxset_parsed() after
                parsing equations into a set of parsed equations.

        **results**:

            * The left-hand-side variable (lhsvar) is the first token.

            * The equals sign is the second token.

            * The following tokens are the right-hand side expression

            * If the right-hand-side expression has 1 token:

                * If the rhs is another complex variable, cxvar, set
                  REAL(lhsvar) and IMAG(lhsvar) to REAL(cxvar) and IMAG(cxvar)

                * If the rhs is a variable, var,  which is already in the
                  data array,
                  set REAL(lhsvar) to var, IMAG(lhsvar) to 0

                * If the rhs is a real number, rnum,
                  set REAL(lhsvar) to rnum, IMAG(lhsvar) to 0

            * If the right-hand-side expression has 2 tokens (unary operation):

                * The first token is the unary operation

                * The second token is either another complex variable,
                  another variable already in the array, or a real number.
 
                * Set REAL(lhsvar), IMAG(lhsvar) to the unary operation of
                  the right-hand side.

                * Supported unary operations are:
                  - sign reciprocal sqrt square abs sin cos tan
                  asin acos atan exp expm1 exp2 log log10 log2 log1p
                  sinh cosh tanh asinh acosh atanh degrees radians
                  deg2rad rad2deg rint fix floor ceil trunc

            * If the right-hand-side expression has 3 tokens (binary operation):

                * The first token is the first operand

                * The second token is the binary operation

                * The third token is the second operand

                * The two operands can be either other complex variables,
                  other variables already in the array, or real numbers.

                * Set REAL(lhsvar), IMAG(lhsvar) to the binary operation
                  of the two operands.

                * Supported binary operations are:
                  + - * / ^ true_divide floor_divide fmod mod rem hypot max min

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.cxset_parsed("z = sqrt gout")
            >>> d.cxset_parsed("z = zout + z")
            >>> d.cxset_parsed("z = abs z")

        """
        m=re.search("^([^=]+)=(.+)$", equation)
        if not m :
            self.warning("equation not in right format: LHS = RHS")
            return
        zcol = m.group(1)
        rhs  = m.group(2)
        zcol= string.strip(zcol)
        rhs = string.strip(rhs)
        tok = string.split(rhs)
        irz, iiz = self.cxreim(zcol, create=True)
        if   len(tok) == 1:
            xc = tok[0]
            irx, iix = self.cxreim(xc, nocomplain=True)
            ixc = self.index(xc)
            if (not irx is None) and (not iix is None) :
                xr = self._data_array[:, irx]
                xi = self._data_array[:, iix]
            elif (not ixc is None) :
                xr = self._data_array[:, ixc]
                xi = 0.0
            else :
                xr = float(xc)
                xi = 0.0
            self._data_array[:, irz] = xr
            self._data_array[:, iiz] = xi
        elif len(tok) == 2:
            op, xc = tok
            irx, iix = self.cxreim(xc, nocomplain=True)
            ixc = self.index(xc)
            if (not irx is None) and (not iix is None) :
                xr = self._data_array[:, irx]
                xi = self._data_array[:, iix]
            elif (not ixc is None) :
                xr = self._data_array[:, ixc]
                xi = 0.0
            else :
                xr = float(xc)
                xi = 0.0
            if op in Data._UnaryOp :
                z = Data._UnaryOp[op](xr + 1j*xi)
                self._data_array[:,irz] = numpy.real(z)
                self._data_array[:,iiz] = numpy.imag(z)
        elif len(tok) == 3:
            yc, op, xc = tok
            irx, iix = self.cxreim(xc, nocomplain=True)
            iry, iiy = self.cxreim(yc, nocomplain=True)
            ixc = self.index(xc)
            iyc = self.index(yc)
            if (not irx is None) and (not iix is None) :
                xr = self._data_array[:, irx]
                xi = self._data_array[:, iix]
            elif (not ixc is None) :
                xr = self._data_array[:, ixc]
                xi = 0.0
            else :
                xr = float(xc)
                xi = 0.0
            if (not iry is None) and (not iiy is None) :
                yr = self._data_array[:, iry]
                yi = self._data_array[:, iiy]
            elif (not iyc is None) :
                yr = self._data_array[:, iyc]
                yi = 0.0
            else :
                yr = float(yc)
                yi = 0.0
            if op in Data._BinaryOp :
                z = Data._BinaryOp[op](yr + 1j*yi, xr + 1j*xi)
                self._data_array[:,irz] = numpy.real(z)
                self._data_array[:,iiz] = numpy.imag(z)
        self.cxmag(zcol)
    #=========================================================================
    # METHOD: cxmag_old
    # PURPOSE: generate magnitude, dB and phase columns
    #=========================================================================
    def __cxmag_old(self, zcol) :
        """ generate magnitude, dB and phase columns."""
        irz, iiz = self.cxreim(zcol)
        if irz == None or iiz == None:
            return
        rz = "REAL(%s)" % (zcol)
        iz = "IMAG(%s)" % (zcol)
        mz = "MAG(%s)"  % (zcol)
        dz = "DB(%s)"   % (zcol)
        pz = "PH(%s)"   % (zcol)
        self.insert(iz, mz, dz, pz)
        imz = self.index(mz)
        idz = self.index(dz)
        ipz = self.index(pz)
        zr = self._data_array[:, irz]
        zi = self._data_array[:, iiz]
        mg = numpy.sqrt(numpy.add(numpy.square(zr), numpy.square(zi)))
        db = 20.0*numpy.log10(numpy.maximum(mg, 1e-300))
        ph = numpy.rad2deg(numpy.unwrap(numpy.arctan2(zi, zr)))
        self._data_array[:, imz] = mg
        self._data_array[:, idz] = db
        self._data_array[:, ipz] = ph
    #=========================================================================
    # METHOD: cxmag
    # PURPOSE: generate magnitude, dB and phase columns
    #=========================================================================
    def cxmag(self, zcol) :
        """ generate magnitude, dB and phase columns.

        **arguments**:

            .. option:: zcol (str)

               column to generate dB and phase columns.
               zcol must be represented by REAL(zcol) and IMAG(zcol).

        **results**:

            * columns MAG(zcol), DB(zcol) and PH(zcol) are generated, using
              REAL(zcol) and IMAG(zcol).

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.cxmag("zout")

        """
        rz = "REAL(%s)" % (zcol)
        iz = "IMAG(%s)" % (zcol)
        mz = "MAG(%s)"  % (zcol)
        dz = "DB(%s)"   % (zcol)
        pz = "PH(%s)"   % (zcol)
        if not rz in self.names() or not iz in self.names() :
            return
        self.insert(iz, mz, dz, pz)
        self.set("%s = sqrt(%s^2 + %s^2)"         % (mz, rz, iz))
        self.set("%s = 20*log10(max(%s, 1e-300))" % (dz, mz))
        self.set("%s = rad2deg(atan2(%s, %s))"    % (pz, iz, rz))
    #=========================================================================
    # METHOD: oneport_YtoS
    # PURPOSE: one-port Y-parameters to S-parameters
    #=========================================================================
    def oneport_YtoS(self, y, s, r0=50.0) :
        """ one-port Y-parameters to S-parameters.

        **arguments**:

            .. option:: y (int or str)

                Y-parameter (complex) variable.  REAL(y) and IMAG(y), etc.
                must exist.

            .. option:: s (str)

                S-parameter (complex) variable to create (or overwrite, if
                already existing).

            .. option:: r0 (float, default=50)

                normal impedance in ohms.

        **results**:

            * The S-parameter columns are created (or overwritten).

            * y0 = 1/r0
              s  = (1-y/y0)/(1+y/y0)

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.oneport_YtoS("Y11", "S11")

        """
        y0 = 1.0/r0
        yn = self.unique_name("yn")
        self.cxset("$yn = $y/$y0")
        self.cxset("$s = (1-$yn)/(1+$yn)")
        self.delete(yn)
    #=========================================================================
    # METHOD: oneport_StoY
    # PURPOSE: one-port S-parameters to Y-parameters
    #=========================================================================
    def oneport_StoY(self, s, y, r0=50.0) :
        """ one-port S-parameters to Y-parameters.

        **arguments**:

            .. option:: s (int or str)

                S-parameter (complex) variable.  REAL(s) and IMAG(s), etc.
                must exist.

            .. option:: y (str)

                Y-parameter (complex) variable to create (or overwrite, if
                already existing).

            .. option:: r0 (float, default=50)

                normal impedance in ohms.

        **results**:

            * The Y-parameter columns are created (or overwritten).

            * y0 = 1/r0
              y = y0*(1-s)/(1+s)

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.oneport_StoY("S11", "Y11")

        """
        y0 = 1/r0
        self.cxset("$y = $y0*(1-$s)/(1+$s)")
    #=========================================================================
    # METHOD: oneport_ZtoS
    # PURPOSE: one-port Z-parameters to S-parameters
    #=========================================================================
    def oneport_ZtoS(self, z, s, r0=50.0) :
        """ one-port Z-parameters to S-parameters.

        **arguments**:

            .. option:: z (int or str)

                Z-parameter (complex) variable.  REAL(z) and IMAG(z), etc.
                must exist.

            .. option:: s (str)

                S-parameter (complex) variable to create (or overwrite, if
                already existing).

            .. option:: r0 (float, default=50)

                normal impedance in ohms.

        **results**:

            * The S-parameter columns are created (or overwritten).

            * s = (z/r0-1)/(z/r0+1)

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.oneport_ZtoS("Z11", "S11")

        """
        zn = self.unique_name("zn")
        self.cxset("$zn = $z/$r0")
        self.cxset("$s = ($zn-1)/($zn+1)")
        self.delete(zn)
    #=========================================================================
    # METHOD: oneport_StoZ
    # PURPOSE: one-port S-parameters to Z-parameters
    #=========================================================================
    def oneport_StoZ(self, s, z, r0=50.0) :
        """ one-port S-parameters to Z-parameters.

        **arguments**:

            .. option:: s (int or str)

                S-parameter (complex) variable.  REAL(s) and IMAG(s), etc.
                must exist.

            .. option:: z (str)

                Z-parameter (complex) variable to create (or overwrite, if
                already existing).

            .. option:: r0 (float, default=50)

                normal impedance in ohms.

        **results**:

            * The Z-parameter columns are created (or overwritten).

            * z = r0*(1+s)/(1-s)

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.oneport_StoZ("S11", "Z11")

        """
        self.cxset("$z = $r0*(1+$s)/(1-$s)")
    #=========================================================================
    # METHOD: twoport_YtoZ
    # PURPOSE: two-port Y-parameters to Z-parameters
    #=========================================================================
    def twoport_YtoZ(self, y11, y12, y21, y22, z11, z12, z21, z22) :
        """ two-port Y-parameters to Z-parameters.

        **arguments**:

            .. option:: y11, y12, y21, y22 (int or str)

                Y-parameter (complex) variables.  REAL(y11) and IMAG(y11), etc.
                must exist.

            .. option:: z11, z12, z21, z22 (str)

                Z-parameter (complex) variables to create (or overwrite, if
                already existing).

        **results**:

            * The Z columns are created (or overwritten).

            * Z = 1/Y (4x4 matrix of complex values)

            * on a matrix-element basis:
              det =  y11*y22-y12*y21
              z11 =  y22/det
              z12 = -y12/det
              z21 = -y21/det
              z22 =  y11/det

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.twoport_YtoZ("Y11", "Y12", "Y21", "Y22", "Z11", "Z12", "Z21", "Z22")

        """
        det = self.unique_name("det")
        self.cxset("$det = $y11*$y22 - $y12*$y21")
        self.cxset("$z11 =  $y22/$det")
        self.cxset("$z12 = -$y12/$det")
        self.cxset("$z21 = -$y21/$det")
        self.cxset("$z22 =  $y11/$det")
        self.delete(det)
    #=========================================================================
    # METHOD: twoport_ZtoY
    # PURPOSE: two-port Z-parameters to Y-parameters
    #=========================================================================
    def twoport_ZtoY(self, z11, z12, z21, z22, y11, y12, y21, y22) :
        """ two-port Z-parameters to Y-parameters.

        **arguments**:

            .. option:: z11, z12, z21, z22 (int or str)

                Z-parameter (complex) variables.  REAL(z11) and IMAG(z11), etc.
                must exist.

            .. option:: y11, y12, y21, y22 (str)

                Y-parameter (complex) variables to create (or overwrite, if
                already existing).

        **results**:

            * The Y columns are created (or overwritten).

            * Y = 1/Z (4x4 matrix of complex values)

            * on a matrix-element basis:
              det =  z11*z22-z12*z21
              y11 =  z22/det
              y12 = -z12/det
              y21 = -z21/det
              y22 =  z11/det

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.twoport_ZtoY("Z11", "Z12", "Z21", "Z22", "Y11", "Y12", "Y21", "Y22")

        """
        det = self.unique_name("det")
        self.cxset("$det = $z11*$z22 - $z12*$z21")
        self.cxset("$y11 =  $z22/$det")
        self.cxset("$y12 = -$z12/$det")
        self.cxset("$y21 = -$z21/$det")
        self.cxset("$y22 =  $z11/$det")
        self.delete(det)
    #=========================================================================
    # METHOD: twoport_YtoH
    # PURPOSE: two-port Y-parameters to H-parameters
    #=========================================================================
    def twoport_YtoH(self, y11, y12, y21, y22, h11, h12, h21, h22) :
        """ two-port Y-parameters to H-parameters.

        **arguments**:

            .. option:: y11, y12, y21, y22 (int or str)

                Y-parameter (complex) variables.  REAL(y11) and IMAG(y11), etc.
                must exist.

            .. option:: h11, h12, h21, h22 (str)

                H-parameter (complex) variables to create (or overwrite, if
                already existing).

        **results**:

            * The H columns are created (or overwritten).

            * on a matrix-element basis:
              h11 =  1/y11
              h12 = -y12/y11
              h21 =  y21/y11
              h22 =  (y11*y22 - y12*y21)/y11

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.twoport_YtoH("Y11", "Y12", "Y21", "Y22", "H11", "H12", "H21", "H22")

        """
        self.cxset("$h11 =     1/$y11") 
        self.cxset("$h12 = -$y12/$y11")
        self.cxset("$h21 =  $y21/$y11")
        self.cxset("$h22 =  ($y11*$y22 - $y21*$y12)/$y11")
    #=========================================================================
    # METHOD: twoport_HtoY
    # PURPOSE: two-port H-parameters to Y-parameters
    #=========================================================================
    def twoport_HtoY(self, h11, h12, h21, h22, y11, y12, y21, y22) :
        """two-port H-parameters to Y-parameters.

        **arguments**:

            .. option:: h11, h12, h21, h22 (int or str)

                H-parameter (complex) variables.  REAL(h11) and IMAG(h11), etc.
                must exist.

            .. option:: y11, y12, y21, y22 (str)

                Y-parameter (complex) variables to create (or overwrite, if
                already existing).

        **results**:

            * The Y columns are created (or overwritten).

            * on a matrix-element basis:
              y11 =  1/h11
              y12 = -h12/h11
              y21 =  h21/h11
              y22 =  (h11*h22 - h12*h21)/h11

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.twoport_HtoY("H11", "H12", "H21", "H22", "Y11", "Y12", "Y21", "Y22")

        """
        self.cxset("$y11 =     1/$h11")
        self.cxset("$y12 = -$h12/$h11")
        self.cxset("$y21 =  $h21/$h11")
        self.cxset("$y22 =  ($h11*$h22 - $h21*$h12)/$h11")
    #=========================================================================
    # METHOD: twoport_YtoS
    # PURPOSE: two-port Y-parameters to S-parameters
    #=========================================================================
    def twoport_YtoS(self, y11, y12, y21, y22, s11, s12, s21, s22, r0=50.0) :
        """ two-port Y-parameters to S-parameters.

        **arguments**:

            .. option:: y11, y12, y21, y22 (int or str)

                Y-parameter (complex) variables.  REAL(y11) and IMAG(y11), etc.
                must exist.

            .. option:: s11, s12, s21, s22 (str)

                S-parameter (complex) variables to create (or overwrite, if
                already existing).

            .. option:: r0 (float, default=50)

                normal impedance in ohms.

        **results**:

            * The S columns are created (or overwritten).

            * on a matrix-element basis:
              yo  =  1/r0
              y11n = y11/y0
              y12n = y12/y0
              y21n = y21/y0
              y22n = y22/y0
              den = (1 + y11n)*(1 + y22n) - y12n*y21n)
              s11 = (1 - y11n)*(1 + y22n) + y12n*y21n)/den
              s22 = (1 + y11n)*(1 - y22n) + y12n*y21n)/den
              s12 = -2*y12n/den
              s21 = -2*y21n/den

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.twoport_YtoS("Y11", "Y12", "Y21", "Y22", "S11", "S12", "S21", "S22")

        """
        y0 = 1/r0
        y11n= self.unique_name("y11n")
        y12n= self.unique_name("y12n")
        y21n= self.unique_name("y21n")
        y22n= self.unique_name("y22n")
        den = self.unique_name("den")
        self.cxset("$y11n = $y11/$y0")
        self.cxset("$y12n = $y12/$y0")
        self.cxset("$y21n = $y21/$y0")
        self.cxset("$y22n = $y22/$y0")
        self.cxset("$den =  (1 + $y11n)*(1 + $y22n) - $y12n*$y21n)")
        self.cxset("$s11 = ((1 - $y11n)*(1 + $y22n) + $y12n*$y21n)/$den")
        self.cxset("$s22 = ((1 + $y11n)*(1 - $y22n) + $y12n*$y21n)/$den")
        self.cxset("$s12 = -2*$y12n/$den")
        self.cxset("$s21 = -2*$y21n/$den")
        self.delete(y11n, y12n, y21n, y22n, den)
    #=========================================================================
    # METHOD: twoport_StoY
    # PURPOSE: two-port S-parameters to Y-parameters
    #=========================================================================
    def twoport_StoY(self, s11, s12, s21, s22, y11, y12, y21, y22, r0=50.0) :
        """ two-port S-parameters to Y-parameters.

        **arguments**:

            .. option:: s11, s12, s21, s22 (int or str)

                S-parameter (complex) variables.  REAL(s11) and IMAG(s11), etc.
                must exist.

            .. option:: y11, y12, y21, y22 (str)

                Y-parameter (complex) variables to create (or overwrite, if
                already existing).

            .. option:: r0 (float, default=50)

                normal impedance in ohms.

        **results**:

            * The Y columns are created (or overwritten).

            * on a matrix-element basis:
              y0 = 1/r0
              den = (1 + s11)*(1 + s22) - s12*s21)
              y11 = y0*((1 - s11)*(1 + s22) + s12*s21))/den
              y22 = y0*((1 + s11)*(1 - s22) + s12*s21))/den
              y12 = y0*(-2*s12)/den
              y21 = y0*(-2*s21)/den

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("spars.col")
            >>> d.twoport_StoY("S11", "S12", "S21", "S22", "Y11", "Y12", "Y21", "Y22")

        """
        y0 = 1/r0
        den = self.unique_name("den")
        self.cxset("$den =      (1 + $s11)*(1 + $s22) - $s12*$s21)")
        self.cxset("$y11 = $y0*((1 - $s11)*(1 + $s22) + $s12*$s21)/$den")
        self.cxset("$y22 = $y0*((1 + $s11)*(1 - $s22) + $s12*$s21)/$den")
        self.cxset("$y12 = $y0*(-2*$s12)/$den")
        self.cxset("$y21 = $y0*(-2*$s21)/$den")
        self.delete(den)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # plot
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #=========================================================================
    # METHOD: plot
    # PURPOSE: plot using matplotlib.pylab
    #=========================================================================
    def plot(self, xcol, *ycol_list, **kwargs) :
        """ plot using matplotlib.pylab.

        **arguments**:

            .. option:: xcol (int or str)

                column of x values of data to plot.
                If xcol is a string, it refers to the column named xcol.

            .. option:: \*ycol_list (tuple)

                columns (str or int) of y values of data to plot.

            .. option:: \*\*kwargs (dict)

                options:

                    * title  : specify plot title.

                    * xtitle : specify plot x-axis title.

                    * ytitle : specify plot y-axis title.

                    * axes   : one of "lin", "log", "lin_lin", "lin_log",
                               "log_lin", or "log_log"

        **results**:

            * X-Y plot of the data columns is displayed.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.plot("time", "v(a)", "v(b)", "v(z)",
            ... xtitle="time", ytitle="signals", axes="lin_lin")

        """
        if not _have_mat :
            return
        axes   = "lin_lin"
        xtitle = None
        ytitle = None
        title  = "data plot"
        for key, val in kwargs.items() :
            if   key == "title" :
                title = val
            elif key == "xtitle" :
                xtitle = val
            elif key == "ytitle" :
                ytitle = val
            elif key == "axes" :
                axes = val
                if not axes in ["lin", "lin_lin", "lin_log", "log", "log_lin", "log_log"] :
                    print "Data::plot: axes should be lin, lin_lin, lin_log, log, log_lin or log_log"
                    return
            else :
                print "option " + key + " not recognized"
        xvals = self.get(xcol)
        xname = self.name(xcol)
        ynames = []
        for ycol in ycol_list :
            yvals = self.get(ycol)
            yname = self.name(ycol)
            ynames.append(yname)
            if   axes == "lin_lin" or axes == "lin":
                plt.plot(xvals, yvals, label=yname)
            elif axes == "lin_log" or axes == "log":
                plt.semilogy(xvals, yvals, label=yname)
            elif axes == "log_lin" :
                plt.semilogx(xvals, yvals, label=yname)
            elif axes == "log_log" :
                plt.loglog(xvals, yvals, label=yname)

        plt.grid()
        if xtitle == None :
            xtitle = xname
        if ytitle == None :
            ytitle = string.join(ynames, ", ")
        plt.xlabel(xtitle)
        plt.ylabel(ytitle)
        plt.legend()
        plt.title("data plot")
        plt.show()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # write
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #=========================================================================
    # METHOD: write_csdf
    # PURPOSE: write csdf file
    #=========================================================================
    def __write_csdf(self, *args) :
        """ write csdf file. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: write_hjou
    # PURPOSE: write hspice journal file
    #=========================================================================
    def __write_hjou(self, *args) :
        """ write hspice journal file. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: write_hspice
    # PURPOSE: write hspice file
    #=========================================================================
    def __write_hspice(self, *args) :
        """ write hspice file. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: write_tsv
    # PURPOSE: write tab-separated value file
    #=========================================================================
    def __write_tsv(self, *args) :
        """ write tab-separated value file. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: write_varval
    # PURPOSE: write variable=value format file
    #=========================================================================
    def __write_varval(self, *args) :
        """ write variable=value file. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: write_vcd_csv
    # PURPOSE: write value-change-dump csv file
    #=========================================================================
    def __write_vcd_csv(self, *args) :
        """ write value-change-dump csv file. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: write_ssv
    # PURPOSE: write ssv file
    #=========================================================================
    def write_ssv(self, ssvfile=None) :
        """ write space-separated value file.

        **arguments**:

            .. option:: ssvfile (string, default=None)

                space-separated value format file to write.
                If None, use dialog to get file name.
            
        **results**:

            * space-separated value format file is written using
              data array data and column-names.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.write_ssv("data1.ssv")

        """
        if ssvfile == None :
            ssvfile = tkFileDialog.asksaveasfilename(title="SSV-format filename to write? ", initialdir=os.getcwd(), defaultextension=".col")
            if not ssvfile :
                return False
        f = open(ssvfile, "w")
        f.write(string.join(self.names(), " ") + "\n")
        for i in range(0, self.nrows()) :
            lout = []
            for x in self._data_array[i,:] :
                lout.append(str(x))
            f.write(string.join(lout, " ") + "\n")
        f.close()
    #=========================================================================
    # METHOD: write_csv
    # PURPOSE: write csv file
    #=========================================================================
    def write_csv(self, csvfile=None, column_limit=None) :
        """ write comma-separated value file.

        **arguments**:

            .. option:: csvfile (string, default=None)

                comma-separated value format file to write.
                If None, use dialog to get file name.
            
            .. option:: column_limit (int, default=None)
            
                limit number of output columns to column_limit.
                If None, there is no limit

        **results**:

            * comma-separated value format file is written using
              data array data and column-names.
              If column_limit is specified, then only
              write up to column_limit columns of data.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.write_csv("data1.csv", column_limit=None)
        """
        if csvfile == None :
            csvfile = tkFileDialog.asksaveasfilename(title="CSV-format filename to write? ", initialdir=os.getcwd(), defaultextension=".csv")
            if not csvfile :
                return False
        f = open(csvfile, "w")
        if not column_limit is None :
           lout = []
           for col in self.names() :
               col = re.sub("\(", "_", col)
               col = re.sub("\)", "", col)
               lout.append(col)
               if len(lout) > column_limit :
                   break
           f.write(string.join(lout, ",") + "\n")
        else :   
           f.write(string.join(self.names(), ",") + "\n")
        for i in range(0, self.nrows()) :
            lout = []
            for x in self._data_array[i,:] :
                lout.append(str(x))
                if (not (column_limit is None) and (len(lout) > column_limit)) :
                    break
            f.write(string.join(lout, ",") + "\n")
        f.close()
    #=========================================================================
    # METHOD: write_nutmeg
    # PURPOSE: write nutmeg file
    # NOTES:
    #=========================================================================
    def write_nutmeg(self, rawfile=None, title="nutmeg data", plotname="decida data", first_vars=False) :
        """ write nutmeg format file.

        **arguments**:

            .. option:: rawfile (string, default=None)

                nutmeg format file to write.
                If None, use dialog to get file name.

            .. option:: title (string, default="nutmeg data")

                data title to place in the nutmeg file.

            .. option:: plotname (string, default="decida data")

                plot name to place in the nutmeg file.

            .. option:: first_vars (bool, default=False)

                if True, put first variables line on the Variables: mode line

        **results**:

            * nutmeg-format file is written using data array data and
              column-names. 
              plotname and title fields are filled into the nutmeg header.

            * if first_vars is specified, variables are written on the
              Variables: line in the nutmeg file.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.write_nutmeg("data.raw", first_vars=True)
        """
        if rawfile == None :
            rawfile = tkFileDialog.asksaveasfilename(title="nutmeg-format filename to write? ", initialdir=os.getcwd(), defaultextension=".raw")
            if not rawfile :
                return False
        timestamp = time.time()
        datetime  = time.asctime(time.localtime(timestamp))
        f = open(rawfile, "w")
        f.write("Title: " + title + "\n")
        f.write("Input deck file name: <NULL> " + "\n")
        f.write("Date: "  + datetime + "\n")
        f.write("Title: " + title + "\n")
        f.write("Plotname: " + plotname + "\n")
        f.write("Temperature: <NULL>" + "\n")
        f.write("Sweepvar: <NULL>" + "\n")
        f.write("Sweepmode: -1" + "\n")
        f.write("Flags: real padded" + "\n")
        f.write("No. Variables: " + str(self.ncols()) + "\n")
        f.write("No. Points: " + str(self.nrows()) + "\n")
        f.write("Source: decida" + "\n")
        f.write("Version: 1.0.2" + "\n")
        for ivar, col in enumerate(self.names()) :
            type = string.upper(col[0])
            if   type == "V" :
                type = "voltage"
            elif type == "I" :
                type = "current"
            else :
                type = "other"
            if ivar == 0 :
                if first_vars :
                    f.write("Variables:")
                else :
                    f.write("Variables:\n")
            f.write("\t" + str(ivar) + "\t" + col + "\t" + type + "\n")
        f.write("Values:" + "\n")
        for i in range(0, self.nrows()) :
            x = self._data_array[i,0]
            f.write(str(i) + "\t" + str(x) + "\n")
            for x in self._data_array[i,1:] :
                f.write("\t" + str(x) + "\n")
            f.write("")
        f.close()
    #=========================================================================
    # METHOD: write_pwl
    # PURPOSE: write piece-wise linear file
    #=========================================================================
    def write_pwl(self, pwlfile=None, *cols) :
        """ write piece-wise linear format file.

        **arguments**:

            .. option:: pwlfile (string, default=None)

                piece-wise linear format file to write.
                If None, use dialog to get file name.

            .. option:: cols (tuple)

                tuple of column names to use to generate the PWL file
                cols = xcol, ycol1, ycol2, ...

        **results**:

            * the piece-wise linear file is a list of xcol, ycol values
              in Spice piece-wise linear format.

            * for each ycol, generate a separate piece-wise linear
              specification.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")
            >>> d.write_pwl("data.pwl", "time v(vc) v(vd)")

        """
        if pwlfile == None :
            pwlfile = tkFileDialog.asksaveasfilename(title="PWL-format filename to write? ", initialdir=os.getcwd(), defaultextension=".pwl")
            if not pwlfile :
                return False
        xcol  = cols[0]
        ycols = cols[1:]
        f = open(pwlfile, "w")
        ixcol = self.index(xcol)
        for ycol in ycols :
            iycol = self.index(ycol)
            vycol = re.sub("\.", "_",  ycol)
            vycol = re.sub("\(", "_", vycol)
            vycol = re.sub("\)",  "", vycol)
            f.write(vycol + " " + vycol + " 0 PWL(" + "\n")
            for i in range(0, self.nrows()) :
                x = self._data_array[i, ixcol]
                y = self._data_array[i, iycol]
                if i < self.nrows() - 1 :
                    f.write("+ " + str(x) + ", " + str(y) + ",\n")
                else :
                    f.write("+ " + str(x) + ", " + str(y) + "\n")
            f.write("+ )\n")
        f.close()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # read
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #=========================================================================
    # METHOD: read
    # PURPOSE: read one of the data formats
    #=========================================================================
    def read(self, file=None, block=0, format=None) :
        """ read data-file in one of the supported data formats.

        **arguments**:

            .. option:: file (string, default=None)

                data file to read.
                If None, use dialog to get file name.

            .. option:: block (int, default=0)

                the block of data within the data-file to read.

            .. option:: format (str, default=None)

                the format of the data-file.  If format=None, use
                Data.datafile_format to try to determine the file format.
                If not None, must be one of:
                "nutmeg", "csdf", "hspice", "csv", "ssv".

        **results**:

            * If data-file format is specified or can be determined, and file
              is in that format, reads data from file and sets the data array
              and column names.

            * If data format cannot be determined, returns None.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read("data.csv")

        """
        if not file :
            file = tkFileDialog.askopenfilename(title="Data File to read?", initialdir=os.getcwd())
            if not file :
                return False
        if not os.path.exists(file) :
            print "data file " + file + " doesn't exist"
            return False
        if not format:
            format = Data.datafile_format(file)
        if not format:
            return False
        if   format == "nutmeg" :
            self.read_nutmeg(file, block=block)
        elif format == "csdf" :
            self.read_csdf(file)
        elif format == "hspice" :
            self.read_hspice(file)
        elif format == "csv" :
            self.read_csv(file, block=block)
        elif format == "ssv" :
            self.read_ssv(file, block=block)
        else :
            return False
    #=========================================================================
    # METHOD: read_inline
    # PURPOSE: read data directly
    #=========================================================================
    def read_inline(self, *args) :
        """ read data directly.

        **arguments**:

            .. option:: \*args (tuple)

               tuple of (name, list or tuple of values) pairs.
               where name is the column to be appended (or rewritten), and
               list or tuple of values is the data for the column.

        **results**:

            * Data is read into the data array.

            * All columns must have the same number of data values.  If not,
              fatal error message is generated.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read_inline("X", (1, 2, 3), "Y", (2, 4, 6))

        """
        nvars = 0
        npts  = 0
        cols  = []
        data  = []
        start = True
        name_data = list(args)
        while len(name_data) > 0 :
            nvars += 1
            col  = name_data.pop(0)
            cols.append(col)
            vals = name_data.pop(0)
            n = len(vals)
            if start :
                start = False
                npts = n
            else :
                if n != npts :
                    self.fatal("column %s length is different from column %s" % (col, cols[0]))
            data.extend(vals)
        a = numpy.zeros(len(data), dtype="float64")
        for i, d in enumerate(data) :
            a[i] = float(d)
        a = a.reshape(nvars, npts)
        self._data_array     = numpy.transpose(a)
        self._data_col_names = cols
        self.title           = ""
    #=========================================================================
    # METHOD: read_inline_ssv
    # PURPOSE: read string of data in ssv format
    #=========================================================================
    def read_inline_ssv(self, ssvlines, block=0) :
        """ read space-separated data string.

        **arguments**:

            .. option:: ssvlines (str)

               string in space-separated value format.

            .. option:: block (int, default=0)

               block of data to read.

        **results**:

            * Data is read into the data array.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> ssvdata = \"\"\"
            ... X Y
            ... 1 2
            ... 2 4
            ... 3 6
            ... \"\"\"
            >>> d.read_inline_ssv(ssvdata)

        """
        lines = string.split(ssvlines, "\n")
        iblock = -1
        fblock = False
        cols = []
        data = []
        npts = 0
        for line in lines :
            line = string.strip(line)
            if line == "" :
                continue
            if re.search("^#", line) :
                continue
            if re.search("^[0-9-]", line) :
                if fblock :
                    npts += 1
                    line = string.split(line)
                    data.extend(line)
                else :
                    # ---------------------------------------------------------
                    # special case: no blocks, no column labels, only numbers
                    # ignore block specification
                    # invent column labels
                    # ---------------------------------------------------------
                    iblock += 1
                    fblock = True
                    npts += 1
                    line = string.split(line)
                    data.extend(line)
                    cols = []
                    cols.append("x")
                    for i, y in enumerate(line[1:]) :
                        cols.append("y%d" % (i))
            else :
                iblock += 1
                if iblock == block :
                    cols = string.split(line)
                    fblock = True
                elif iblock > block :
                    break
        if not fblock :
            print "block " + str(block) + " not found"
            return False
        nvars = len(cols)
        if nvars == 0 or npts == 0 :
            print "problem reading SSV data"
            return(False)
        try :
            a = numpy.zeros(npts*nvars, dtype="float64")
            for i, d in enumerate(data) :
                a[i] = string.atof(d)
        except :
            print "problem reading SSV data"
            return(False)
        self._data_array     = a.reshape(npts, nvars)
        self._data_col_names = cols
        self.title           = ""
    #=========================================================================
    # METHOD: read_ssv
    # PURPOSE: read space-separated file
    #=========================================================================
    def read_ssv(self, ssvfile=None, block=0) :
        """ read space-separated value file.

        **arguments**:

            .. option:: ssvfile (string, default=None)

                data file to read.
                If None, use dialog to get file name.

            .. option:: block (int, default=0)

                the block of data within the data-file to read.

        **results**:

            * Reads data from file and sets the data array
              and column names.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read_ssv("data.ssv")

        """
        if not ssvfile :
            ssvfile = tkFileDialog.askopenfilename(title="SSV-format File to read?", initialdir=os.getcwd(), defaultextension=".col")
            if not ssvfile :
                return False
        if not os.path.exists(ssvfile) :
            print "SSV-format file " + ssvfile + " doesn't exist"
            return False
        f = open(ssvfile, "r")
        iblock = -1
        fblock = False
        cols = []
        data = []
        npts = 0
        for line in f :
            line = string.strip(line)
            if line == "" :
                continue
            if re.search("^#", line) :
                continue
            if re.search("^[0-9+-]", line) :
                if fblock :
                    npts += 1
                    line = string.split(line)
                    data.extend(line)
                else :
                    # ---------------------------------------------------------
                    # special case: no blocks, no column labels, only numbers
                    # ignore block specification
                    # invent column labels
                    # ---------------------------------------------------------
                    iblock += 1
                    fblock = True
                    npts += 1
                    line = string.split(line)
                    data.extend(line)
                    cols = []
                    cols.append("x")
                    for i, y in enumerate(line[1:]) :
                        cols.append("y%d" % (i))
            else :
                iblock += 1
                if iblock == block :
                    cols = string.split(line)
                    fblock = True
                elif iblock > block :
                    break
        if not fblock :
            print "block " + str(block) + " not found in " + ssvfile
            return False
        nvars = len(cols)
        if nvars == 0 or npts == 0 :
            print "problem reading SSV file"
            return(False)
        try :
            a = numpy.zeros(npts*nvars, dtype="float64")
            for i, d in enumerate(data) :
                a[i] = string.atof(d)
        except :
            print "problem reading SSV file"
            return(False)
        self._data_array     = a.reshape(npts, nvars)
        self._data_col_names = cols
        self.title           = ""
    #=========================================================================
    # METHOD: read_csv
    # PURPOSE: read csv file
    #=========================================================================
    def read_csv(self, csvfile=None, block=0) :
        """ read comma-separated value file.

        **arguments**:

            .. option:: csvfile (string, default=None)

                data file to read.
                If None, use dialog to get file name.

            .. option:: block (int, default=0)

                the block of data within the data-file to read.

        **results**:

            * Reads data from file and sets the data array
              and column names.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read_ssv("data.csv")

        """
        if not csvfile :
            csvfile = tkFileDialog.askopenfilename(title="CSV-format File to read?", initialdir=os.getcwd(), defaultextension=".csv")
            if not csvfile :
                return False
        if not os.path.exists(csvfile) :
            print "CSV-format file " + csvfile + " doesn't exist"
            return False
        f = open(csvfile, "r")
        iblock = -1
        fblock = False
        cols = []
        data = []
        npts = 0
        for line in f :
            line = string.strip(line)
            if line == "" :
                continue
            if re.search("^#", line) :
                continue
            if re.search("^[0-9-.,]", line) :
                if fblock :
                    npts += 1
                    line = string.split(line, ",")
                    # a little hacking to replace null entries with 0
                    xline = []
                    for x in line :
                        if x == "" :
                            x = 0
                        xline.append(x)
                    data.extend(xline)
            else :
                iblock += 1
                if iblock == block :
                    line = re.sub(" ", "_", line)
                    line = re.sub("\"", "", line)
                    cols = string.split(line, ",")
                    fblock = True
                elif iblock > block :
                    break
        if not fblock :
            print "block " + str(block) + " not found in " + csvfile
            return False
        nvars = len(cols)
        if nvars == 0 or npts == 0 :
            print "problem reading CSV file"
            return(False)
        try :
            a = numpy.zeros(npts*nvars, dtype="float64")
            for i, d in enumerate(data) :
                a[i] = string.atof(d)
        except :
            print "problem reading CSV file"
            return(False)
        self._data_array     = a.reshape(npts, nvars)
        self._data_col_names = cols
        self.title           = ""
    #=========================================================================
    # METHOD: read_nutmeg
    # PURPOSE: read spice rawfile
    # NOTES:
    #    * adapted from the read_spice module from
    #      Werner Hoch <werner.ho@gmx.de>
    #    * copyright notice / GPL2 terms appearing in read_spice:
    #
    #     Copyright (C) 2007,2011 Werner Hoch
    #
    #    This program is free software; you can redistribute it and/or modify
    #    it under the terms of the GNU General Public License as published by
    #    the Free Software Foundation; either version 2 of the License, or
    #    (at your option) any later version.
    #
    #    This program is distributed in the hope that it will be useful,
    #    but WITHOUT ANY WARRANTY; without even the implied warranty of
    #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #    GNU General Public License for more details.
    #
    #    You should have received a copy of the GNU General Public License
    #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    #
    #=========================================================================
    def read_nutmeg(self, rawfile=None, block=0) :
        """ read nutmeg-format format (spice rawfile).

        **arguments**:

            .. option:: rawfile (string, default=None)

                data file to read.
                If None, use dialog to get file name.

            .. option:: block (int, default=0)

                the block of data within the data-file to read.

        **results**:

            * Reads data from file and sets the data array
              and column names.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read_nutmeg("data.raw")

        """
        ##-- cython syntax:
        #cdef int i, nvars, npts, nvalues
        #cdef numpy.ndarray[DTYPE_t, ndim=1] a
        ##--
        # (read-in) plot attributes:
        col_names      = []
        col_types      = []
        col_cxvars     = []
        title          = ""
        date           = ""
        plotname       = ""
        plottype       = ""
        simulator      = "generic"
        #imulator      = "spectre"
        nvars          = 0
        npts           = 0
        numdims        = 0
        option         = ""
        command        = ""
        offset         = 0.0
        backannotation = ""
        input_deck     = ""
        temperature    = 0.0
        sweepvar       = ""
        sweepmode      = ""
        source         = ""
        version        = ""
        # (read-in) plot flags:
        real           = True
        padded         = True
        forward        = False
        log            = False
        if not rawfile :
            rawfile = tkFileDialog.askopenfilename(title="nutmeg-format File to read?", initialdir=os.getcwd(), defaultextension=".raw")
            if not rawfile :
                return False
        if not os.path.exists(rawfile) :
            print "nutmeg-format file " + rawfile + " doesn't exist"
            return False
        f = open(rawfile, "rb")
        iblock = -1
        while (True):
            line = f.readline()
            if line == "":
                break
                #continue
            tok = [string.strip(t) for t in string.split(line,":",1)]
            keyword = tok[0].lower()
            if   keyword == "title":
                title = tok[1]
                if re.search("spectre", title) :
                    simulator = "spectre"
            elif keyword == "date":
                date  = tok[1]
            elif keyword == "plotname":
                iblock += 1
                plotname = tok[1]
                col_names  = []
                col_types  = []
                col_cxvars = []
            elif keyword == "plottype":
                plottype = tok[1]
            elif keyword == "flags":
                ftok= [string.lower(string.strip(t)) for t in string.split(tok[1])]
                for flag in ftok:
                    if   flag == "real":
                        real = True
                    elif flag == "complex":
                        real = False
                    elif flag == "unpadded":
                        padded = False
                    elif flag == "padded":
                        padded = True
                    elif flag == "forward":
                        forward = True
                    elif flag == "log":
                        log = True
                    else:
                        print 'Warning: unknown flag: "' + flag + '"'
            elif keyword == "no. variables":
                nvars = string.atoi(tok[1])
            elif keyword == "no. points":
                npts = string.atoi(tok[1])
                ## Spectre: dcop dataset can have npts=0
                if False   and npts == 0:
                    npts = 1
            elif keyword == "dimensions":
                numdims = string.atoi(tok[1])
            elif keyword == "option":
                option = tok[1]
            elif keyword == "command":
                ## LTspice
                command = tok[1]
                if re.search("LTspice", command) :
                    simulator = "LTspice"
            elif keyword == "offset":
                ## LTspice
                offset = string.atof(tok[1])
            elif keyword == "backannotation":
                ## LTspice
                backannotation = tok[1]
            elif keyword == "input deck file name":
                ## SmartSpice
                input_deck = tok[1]
            elif keyword == "temperature":
                ## SmartSpice
                temperature = string.atof(tok[1])
            elif keyword == "sweepvar":
                ## SmartSpice
                sweepvar = tok[1]
            elif keyword == "sweepmode":
                ## SmartSpice
                sweepmode = tok[1]
            elif keyword == "source":
                ## SmartSpice
                source = tok[1]
                if re.search("SmartSpice", source) :
                    simulator = "SmartSpice"
            elif keyword == "version":
                ## SmartSpice
                version = tok[1]
            elif keyword == "variables":
                for ivar in range(nvars) :
                    if ivar == 0 and len(tok[1]) > 0:
                      ## SmartSpice starts variable list on this line:
                      ltok = string.split(string.strip(tok[1]))
                    else :
                      ltok = string.split(string.strip(f.readline()))
                    if len(ltok) >= 3:
                        var_num  = string.atoi(ltok[0])
                        var_name = ltok[1]
                        var_type = ltok[2]
                        var_attr = []
                        if len(ltok) > 3 :
                            # ? min, max, color, grid, plot, dim ?
                            var_attr = ltok[3:]
                        if real :
                            col_names.append(var_name)
                            col_types.append(var_type)
                        else :
                            col_cxvars.append(var_name)
                            col_names.append("REAL(" + var_name + ")")
                            col_names.append("IMAG(" + var_name + ")")
                            col_types.append(var_type)
                            col_types.append(var_type)
                    else :
                        print "problem in variable specification:", str(ltok)
                        return(False)
            elif keyword in ["values", "binary"]:
                if real:
                    nvalues = npts*nvars
                    if keyword == "values":
                        a = numpy.zeros(nvalues, dtype="float64")
                        if simulator in ["spectre"] :
                            i = 0
                            while (i < nvalues):
                                j = 0
                                while (j < nvars) :
                                    t = string.split(f.readline())
                                    if j == 0 :
                                        t.pop(0)
                                    for item in t:
                                        a[i] = string.atof(item)
                                        j += 1
                                        i += 1
                        else :
                            i = 0
                            while (i < nvalues):
                                t = string.split(f.readline())
                                if   len(t) == 1 or len(t) == 2 :
                                    a[i] = string.atof(t[-1])
                                    i += 1
                                else:
                                    # blank or over-specified lines ?
                                    continue
                    else: ## keyword = "binary"
                        if simulator in ["LTspice"] :
                            # time is double, voltage/current are float
                            a = numpy.zeros(nvalues, dtype="float64")
                            i = 0
                            while (i < nvalues):
                                time = numpy.frombuffer(f.read(8), dtype="float64")
                                # if compressed, some times are negative ?
                                a[i] = abs(time[0])
                                i += 1
                                sigs = numpy.frombuffer(f.read((nvars - 1)*4), dtype="float32")
                                for sig in sigs :
                                    a[i] = sig
                                    i += 1
                        elif simulator in ["spectre"] :
                            dx = numpy.dtype("float64").newbyteorder('S')
                            if npts==0 :
                                # ignore npts and read entire file
                                print "partial file: ignoring number of points = 0 specification"
                                a = numpy.frombuffer(f.read(), dtype=dx)
                                npts = len(a) / nvars
                                nvalues = npts * nvars
                                a = a[0:nvalues]
                            else :
                                a = numpy.frombuffer(f.read(nvalues*8), dtype=dx)
                        else :
                            a = numpy.frombuffer(f.read(nvalues*8), dtype="float64")
                    if (iblock == block) :
                        self.title           = title
                        self._data_array     = a.reshape(npts,nvars)
                        self._data_col_names = col_names
                        f.close()
                        return()
                else: # complex data
                    nvalues = 2*npts*nvars
                    if keyword == "values":
                        a = numpy.zeros(nvalues, dtype="float64")
                        i = 0
                        while (i < nvalues):
                            t = string.split(f.readline())
                            if   len(t) == 1 or len(t) == 2 :
                                t = string.split(t[-1], ",")
                                a[i] = string.atof(t[0])
                                i += 1
                                a[i] = string.atof(t[1])
                                i += 1
                            else:
                                # blank or over-specified lines ?
                                continue
                    else: ## keyword = "binary"
                        if simulator in ["spectre"] :
                            dx = numpy.dtype("float64").newbyteorder('S')
                            a = numpy.frombuffer(f.read(nvalues*8), dtype=dx)
                        else :
                            a = numpy.frombuffer(f.read(nvalues*8), dtype="float64")
                    if (iblock == block) :
                        self.title           = title
                        self._data_array     = a.reshape(npts,nvars*2)
                        self._data_col_names = col_names
                        #-----------------------------------------------------
                        # add MAG, DB, PH columns
                        # frequency column is real,imag only use real
                        #-----------------------------------------------------
                        for cxvar in col_cxvars :
                            if cxvar in ["frequency", "freq"] :
                                self.name("REAL(%s)" % (cxvar), cxvar)
                                self.delete("IMAG(%s)" % (cxvar))
                            else :
                                self.cxmag(cxvar)
                        f.close()
                        return()

            elif string.strip(keyword) == "":
                continue
            else:
                print 'Warning: unrecognized line in rawfile:\n\t"'  + line
                continue
    #=========================================================================
    # METHOD: read_csdf
    # PURPOSE: read csdf file
    #=========================================================================
    def read_csdf(self, csdffile=None) :
        """ read CSDF-format format.

        **arguments**:

            .. option:: csdffile (string, default=None)

                data file to read.
                If None, use dialog to get file name.

        **results**:

            * Reads data from file and sets the data array
              and column names.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read_csdf("data.csdf")

        """
        if not csdffile :
            csdffile = tkFileDialog.askopenfilename(title="CSDF-format File to read?", initialdir=os.getcwd(), defaultextension=".csdf")
            if not csdffile :
                return False
        if not os.path.exists(csdffile) :
            print "CSDF-format file " + csdffile + " doesn't exist"
            return False
        f = open(csdffile, "rb")

        Info = {}
        cols = []
        data = []
        npts = 0
        cxvalues = False
        col_cxvars = []
        mode = "off"
        for line in f :
            line = string.strip(line, "\n")
            line = string.strip(line)
            tok  = string.split(line)
            if len(tok) == 0 :
                continue
            elif tok[0] == "#H" :
                tok.pop(0)
                mode = "header"
            elif tok[0] == "#N" :
                tok.pop(0)
                mode = "names"
                cols = []
                if "SWEEPVAR" in Info :
                    cols.append(string.lower(Info["SWEEPVAR"]))
                if "TEMPERATURE" in Info :
                    cols.append("temperature")
                tok = map(lambda x: re.sub("'", "", x), tok)
                cxvalues = False
                if "COMPLEXVALUES" in Info :
                    if Info["COMPLEXVALUES"] == "YES" :
                       cxvalues = True
                if cxvalues :
                    for col in tok:
                        col_cxvars.append(col)
                        cols.append("REAL(%s)" % (col))
                        cols.append("IMAG(%s)" % (col))
                else :
                    cols.extend(tok)
            elif tok[0] == "#C" :
                tok.pop(0)
                mode = "data"
                npts += 1
                val  = tok[0]
                ncol = tok[1]
                tok.pop(0)
                tok.pop(0)
                data.append(val)
                if "TEMPERATURE" in Info :
                    data.append(Info["TEMPERATURE"])
                if cxvalues : 
                    for r, s, i in zip(tok[:-2:3], tok[1:-1:3], tok[2::3]) :
                        data.append(r)
                        data.append(i)
                else :
                    data.extend(tok)
            elif tok[0] == "#;" :
                mode = "end"
                break
            elif mode == "header" :
                line = re.sub(" *= *'", ",", line)
                line = re.sub("' *",    ",", line)
                tok = string.split(line, ",")
                for var, val in zip(tok[:-1:2], tok[1::2]) :
                    Info[var] = val
            elif mode == "names" :
                tok = map(lambda x: re.sub("'", "", x), tok)
                if cxvalues :
                    for col in tok:
                        col_cxvars.append(col)
                        cols.append("REAL(%s)" % (col))
                        cols.append("IMAG(%s)" % (col))
                else :
                    cols.extend(tok)
            elif mode == "data" :
                if cxvalues : 
                    for r, s, i in zip(tok[:-2:3], tok[1:-1:3], tok[2::3]) :
                        data.append(r)
                        data.append(i)
                else :
                    data.extend(tok)
            elif mode == "off" :
                pass
            elif mode == "end" :
                break
        nvars = len(cols)
        if nvars == 0 or npts == 0 :
            print "problem reading CSDF file"
            return(False)
        try :
            a = numpy.zeros(npts*nvars, dtype="float64")
            for i, d in enumerate(data) :
                a[i] = string.atof(d)
        except :
            print "problem reading CSDF file"
            return(False)
        self._data_array     = a.reshape(npts, nvars)
        self._data_col_names = cols
        self.title           = ""
        if "TITLE" in Info :
            self.title = Info["TITLE"]
        if cxvalues :
            for cxvar in col_cxvars :
                self.cxmag(cxvar)
        f.close()
    #=========================================================================
    # METHOD: read_hspice
    # PURPOSE: read HSpice-format file (.tr0, .ac0)
    #=========================================================================
    def read_hspice(self, hspicefile) :
        """ read HSpice-format file (.tr0, .ac0).

        **arguments**:

            .. option:: hspicefile (string, default=None)

                data file to read.
                If None, use dialog to get file name.

        **results**:

            * Reads data from file and sets the data array
              and column names.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read_hspice("cmf.tr0")

        """
        if not hspicefile :
            hspicefile = tkFileDialog.askopenfilename(title="HSpice-format File to read?", initialdir=os.getcwd(), defaultextension=".tr0")
            if not hspicefile :
                return False
        if not os.path.exists(hspicefile) :
            print "HSpice-format file " + hspicefile + " doesn't exist"
            return False
        #----------------------
        # see if it is binary:
        #----------------------
        stamp = "00010003000000009601"
        stamp = "00040000000000009601"
        stamp = "000"
        f = open(hspicefile, "rb")
        chars = numpy.frombuffer(f.read(len(stamp)), dtype="int8")
        file_type = "ascii"
        for c, a in zip(chars, stamp) :
            if c != ord(a) :
                file_type = "binary"
                break
        f.seek(0, 0)
        if self["verbose"]:
            print "file, file_type = ", hspicefile, file_type
        #----------------------
        # read data file
        #----------------------
        title = ""
        col_cxvars = []
        cols = []
        data = []
        #----------------------
        # binary
        #----------------------
        if file_type == "binary" :
            #------------------------------
            # limits:
            # 4
            # 2e=(number of bytes/8)
            # 4
            # 170=number of bytes
            #------------------------------
            limits    = numpy.frombuffer(f.read(4*4), dtype="int32")
            header    = f.read(limits[3])
            title     = header[24:88]
            datetime  = header[88:264]
            tok       = string.split(datetime)
            datetime  = tok[0]
            colstring = header[264:]
            while(True) :
                try :
                    #------------------------------
                    # 170=number of previous bytes
                    #------------------------------
                    nprev  = numpy.frombuffer(f.read(4),   dtype="int32")
                    #------------------------------
                    # limits:
                    # 4
                    # 34=number of float32
                    # 4
                    # d0=number of bytes
                    #------------------------------
                    limits = numpy.frombuffer(f.read(4*4), dtype="int32")
                    if len(limits) < 4 : break
                except:
                    break
                ndat = limits[1]
                dataline = numpy.frombuffer(f.read(4*ndat), dtype="float32")
                data.extend(dataline)
        else :
        #----------------------
        # ascii
        #----------------------
            mode  = "header1"
            for line in f :
                line = string.strip(line, "\n")
                tok  = string.split(line)
                if   mode == "header1":
                    prefix = tok[0]
                    title = string.join(tok[1:])
                    mode = "header2"
                elif mode == "header2":
                    datetime = tok[0]
                    mode = "header3"
                elif mode == "header3":
                    mode = "header4"
                elif mode == "header4":
                    colstring = line
                    mode = "names"
                elif mode == "names":
                    colstring += line
                    if re.search("\$\&\%\#", line) :
                        mode = "data"
                elif mode == "data":
                    i1, i2 = 0, 10
                    while i2 < len(line) :
                        val = line[i1:i2+1]
                        data.append(val)
                        i1 += 11
                        i2 += 11
        #-----------------------------------------------
        # binary and ascii
        #-----------------------------------------------
        f.close()
        #---------------------------------
        # extract names from column string
        #---------------------------------
        if self["verbose"]:
            print "colstring = ", colstring
        m = re.search("^([0-9 ]+)(.*)\$\&\%\#", colstring)
        if m :
            flags = string.split(m.group(1))
            flags = [int(flag) for flag in flags]
            colstring = m.group(2)
        else :
            print "problem reading HSpice file"
            print " (reading columns)"
            return(False)
        cols = []
        i1, i2 = 0, 15
        while i2 < len(colstring) :
            item = string.strip(colstring[i1:i2+1])
            cols.append(item)
            i1 += 16
            i2 += 16
        #-----------------------------------------
        # cxvalues: generate real and imag columns
        #-----------------------------------------
        cxvalues = False
        if flags[0] == 2:
            cxvalues = True
        if self["verbose"]:
            print "flags    = ", flags
            print "columns  = ", cols
            print "cxvalues = ", cxvalues
        if cxvalues :
            newcols = []
            newcols.append(cols[0])
            for flag, col in zip(flags[1:], cols[1:]) :
                if flag == 1 or flag == 8 :
                    col_cxvars.append(col)
                    newcols.append("REAL(%s)" % (col))
                    newcols.append("IMAG(%s)" % (col))
                else :
                    newcols.append(col)
            cols = newcols
            if self["verbose"]:
               print "added complex columns:"
               print "columns = ", cols
        #------------------------
        # last data entry is 1e30
        #------------------------
        data.pop()
        nvars = len(cols)
        npts  = len(data) / len(cols)
        if self["verbose"]:
            print "nvars, ndata, npts = ", nvars, len(data), npts
        if nvars == 0 or npts == 0 :
            print "problem reading HSpice file"
            print " (number of variables or data points is 0)"
            return(False)
        try :
            a = numpy.zeros(npts*nvars, dtype="float64")
            for i, d in enumerate(data) :
                a[i] = string.atof(d)
        except :
            print "problem reading HSpice file"
            print " (re-shaping data array)"
            return(False)
        self._data_array     = a.reshape(npts, nvars)
        self._data_col_names = cols
        self.title           = title
        if cxvalues :
            for cxvar in col_cxvars :
                self.cxmag(cxvar)
    #=========================================================================
    # METHOD: read_utmost (IV)
    # PURPOSE: read utmost file
    #=========================================================================
    def read_utmost(self, utmostfile=None, block=0) :
        """ read utmost file.

        **arguments**:

            .. option:: utmostfile (str, default=None)

                data file to read.
                If None, use dialog to get file name.

            .. option:: block (int, default=0)

                the block of data within the data-file to read.

        **results**:

            * Reads data from file and sets the data array
              and column names.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read_utmost("nmos.utm")

        """
        if not utmostfile :
            utmostfile = tkFileDialog.askopenfilename(title="UTMOST-IV-format File to read?", initialdir=os.getcwd(), defaultextension=".uds")
            if not utmostfile :
                return False
        if not os.path.exists(utmostfile) :
            print "UTMOST-IV-format file " + utmostfile + " doesn't exist"
            return False
        f = open(utmostfile, "r")
        iblock = -1
        fblock_found = False
        mode = "header1"
        inps = []
        inp_order  = {}
        inp_values = {}
        outs = []
        out_values = {}
        for line in f :
            line = string.strip(line)
            if line == "" :
                continue
            if   mode == "header1" :
                header1 = line
                mode    = "header2"
            elif mode == "header2" :
                header2 = line
                mode    = "header3"
            elif mode == "header3" :
                header3 = line
                mode    = "null"
            elif mode == "null" :
                if re.search("^DataSetStart", line) :
                    iblock += 1
                    if iblock == block :
                         fblock_found = True
                         mode = "data_header"
            elif mode == "list_header" :
                pars = [string.strip(p) for p in string.split(line, ",")]
                if pars[0] == "List" :
                    nlist = string.atoi(pars[1])
                    ilist = 0
                    inp_values[inp] = []
                    mode = "list_lines"
                else :
                    print "problem with list format"
                    exit()
            elif mode == "list_lines" :
                ilist += 1
                if ilist >= nlist :
                    mode = "data_header"
                else :
                    inp_values[inp].extend(string.split(line))
            elif mode == "data_header" :
                if re.search("^Sweep,", line) :
                    pars = [string.strip(p) for p in string.split(line, ",")]
                    inp  = pars[3]
                    inps.append(inp)
                    flag = pars[4]           # LIN LIST
                    inp_order[inp] = pars[1] # primary or secondary step
                    if flag == "LIN" :
                        vmin = string.atof(pars[5])
                        vmax = string.atof(pars[6])
                        step = string.atof(pars[7])
                        inp_values[inp] = \
                            decida.range_sample(vmin, vmax, step=step)
                    elif flag == "LIST" :
                        mode = "list_header"
                elif re.search("^Constant,", line) :
                    pars = [string.strip(p) for p in string.split(line, ",")]
                    inp  = pars[2]
                    inps.append(inp)
                    inp_order[inp]  = "0"
                    inp_values[inp] = [string.atof(pars[3])]
                elif re.search("^DataArray", line) :
                    pars = [string.strip(p) for p in string.split(line, ",")]
                    out  = pars[1]
                    outs.append(out)
                    out_values[out] = []
                    mode = "data"
            elif mode == "data" :
                if re.search("^[0-9-]", line) :
                    out_values[out].extend(
                        [string.atof(p) for p in string.split(line)])
                elif re.search("^DataArray", line) :
                    pars = [string.strip(p) for p in string.split(line, ",")]
                    out  = pars[1]
                    outs.append(out)
                    out_values[out] = []
                    mode = "data"
                elif re.search("^DataSetFinish", line) :
                    mode = "null"
                    break
        if not fblock_found :
            print "block " + str(block) + " not found in " + utmostfile
            return False
        nvars = len(outs)

        inp1 = None
        inp2 = None
        inp3 = None
        inp4 = None
        for inp in inps :
            if   inp_order[inp] == "1" :
               inp1 = inp
            elif inp_order[inp] == "2" :
               inp2 = inp
            elif inp_order[inp] == "0" :
               if   inp2 == None :
                   inp2 = inp
               elif inp3 == None :
                   inp3 = inp
               elif inp4 == None :
                   inp4 = inp
        cols = []
        data = []
        npts = 0;
        if inp4 != None:
            for inp in [inp1, inp2, inp3, inp4] :
                cols.append("V(" + inp + ")")
            for out in outs :
                cols.append(out)
            for val4 in inp_values[inp4] :
                for val3 in inp_values[inp3] :
                    for val2 in inp_values[inp2] :
                        for val1 in inp_values[inp1] :
                            npts += 1
                            data.append(val1)
                            data.append(val2)
                            data.append(val3)
                            data.append(val4)
                            for out in outs :
                                data.append(out_values[out][npts-1])
        elif inp3 != None:
            for inp in [inp1, inp2, inp3] :
                cols.append("V(" + inp + ")")
            for out in outs :
                cols.append(out)
            for val3 in inp_values[inp3] :
                for val2 in inp_values[inp2] :
                    for val1 in inp_values[inp1] :
                        npts += 1
                        data.append(val1)
                        data.append(val2)
                        data.append(val3)
                        for out in outs :
                            data.append(out_values[out][npts-1])
        elif inp2 != None:
            for inp in [inp1, inp2] :
                cols.append("V(" + inp + ")")
            for out in outs :
                cols.append(out)
            for val2 in inp_values[inp2] :
                for val1 in inp_values[inp1] :
                    npts += 1
                    data.append(val1)
                    data.append(val2)
                    for out in outs :
                        data.append(out_values[out][npts-1])
        elif inp1 != None :
            for inp in [inp1] :
                cols.append("V(" + inp + ")")
            for out in outs :
                cols.append(out)
            for val1 in inp_values[inp1] :
                npts += 1
                data.append(val1)
                for out in outs :
                    data.append(out_values[out][npts-1])

        nvars = len(cols)
        if nvars == 0 or npts == 0 :
            print "problem reading UTMOST-IV file"
            return(False)
        try :
            a = numpy.zeros(npts*nvars, dtype="float64")
            for i, d in enumerate(data) :
                a[i] = string.atof(d)
        except :
            print "problem reading UTMOST-IV file"
            return(False)
        self._data_array     = a.reshape(npts, nvars)
        self._data_col_names = cols
        self.title           = ""
    #=========================================================================
    # METHOD: read_psf
    # PURPOSE: read cadence PSF ASCII format
    #=========================================================================
    def read_psf(self, psffile=None) :
        """ read PSF-ASCII file.

        **arguments**:

            .. option:: psffile (str, default=None)

                data file to read.
                If None, use dialog to get file name.

        **results**:

            * Reads data from file and sets the data array
              and column names.

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read_psf("mckt.psf")

        """
        if not psffile :
            psffile = tkFileDialog.askopenfilename(title="PSF-ASCII-format File to read?", initialdir=os.getcwd(), defaultextension=".tran")
            if not psffile :
                return False
        if not os.path.exists(psffile) :
            print "PSF-ASCII-format file " + psffile + " doesn't exist"
            return False
        f = open(psffile, "rb")

        Info = {}
        cols = []
        data = []
        npts = 0
        complex = False
        Cx_var = {}
        scol = ""
        icol = -1
        mode = "OFF"
        start = False
        psf_modes = ("HEADER", "TYPE", "SWEEP", "TRACE", "VALUE", "END")
        for line in f :
            line = string.strip(line, "\n")
            line = string.strip(line)
            tok  = string.split(line)
            if len(tok) == 0 :
                continue
            if (mode == "OFF" and tok[0] == "HEADER") or \
               (mode != "OFF" and tok[0] in psf_modes)  :
                mode = tok[0]
                start = True
            elif mode == "HEADER" :
                var, val = tok[0:2]
                var = re.sub("\"", "", var)
                val = re.sub("\"", "", val)
                cols.append(var)
                Info[var] = val
            elif mode == "VALUE" :
                #---------------------------------
                # remove () for real, imag
                #---------------------------------
                line = re.sub("[()]", "", line)
                tok  = string.split(line)
                #---------------------------------
                # dc op output has unit in center:
                #---------------------------------
                if len(tok) == 3 and re.search("^[VI]", tok[1]) :
                    tok.pop(1)
                #---------------------------------
                # tran or dcop or ac
                #---------------------------------
                if   len(tok) == 2:
                    complex  = False
                    var, val = tok[0:2]
                elif len(tok) == 3:
                    complex  = True
                    Cx_var[var] = 1
                    var, val, ival = tok[0:3]
                var = re.sub("\"", "", var)
                if start :
                    scol = var
                    start = False
                if var == scol :
                    npts += 1
                    icol = -1
                #--------------------------------------------------
                # look for var in list of columns
                # if not found, could have been specified in HEADER
                # not sure if time, freq are specified in header, so
                #   else block inserts it
                #--------------------------------------------------
                icol += 1
                while icol < len(cols) :
                    if var != cols[icol] :
                        if var in Info :
                            data.append(float(Info[var]))
                        else :
                            cols.insert(icol, var)
                            data.append(float(val))
                            break
                    else :
                        data.append(float(val))
                        if complex :
                            data.append(float(ival))
                        break
        f.close()
        #----------------------------------------------------------------------
        # add complex columns
        #----------------------------------------------------------------------
        if len(Cx_var.keys()) > 0 :
            new_cols = []
            for col in cols :
                if col in Cx_var :
                    new_cols.append("REAL(%s)" % (col))
                    new_cols.append("IMAG(%s)" % (col))
                else :
                    new_cols.append(col)
            cols = new_cols
        #----------------------------------------------------------------------
        # might be necessary to remove last data record if it is incomplete
        #----------------------------------------------------------------------
        #----------------------------------------------------------------------
        # reshape data
        #----------------------------------------------------------------------
        nvars = len(cols)
        if nvars == 0 or npts == 0 :
            print "problem reading PSF-ASCII file"
            return(False)
        try :
            a = numpy.zeros(npts*nvars, dtype="float64")
            for i, d in enumerate(data) :
                a[i] = string.atof(d)
        except :
            print "problem reading PSF-ASCII file"
            return(False)
        self._data_array     = a.reshape(npts, nvars)
        self._data_col_names = cols
        self.title           = ""
        #----------------------------------------------------------------------
        # magnitude, dB and phase columns for complex variables
        #----------------------------------------------------------------------
        for col in Cx_var :
            self.cxmag(col)
    #=========================================================================
    # METHOD: read_sspar
    # PURPOSE: read Cadence Spectre S-parameter file
    #=========================================================================
    def read_sspar(self, file=None) :
        """ read Cadence Spectre S-parameter file.

        **arguments**:

            .. option:: file (string, default=None)

                Cadence Spectre S-parameter file.
                If file is None, get file from dialog.

        **notes**:

            * Currently, Data:read_spectre_spars only supports the
              (real,imag) format

            * The : separator in s-parameter names is removed if the
              ports have one digit. For example, S1:1 is changed to S11.

            * A description of the Cadence Spectre S-parameter file format
              is at: 

              http://www.ece.tufts.edu/~srout01/doc/manuals/spectreuser/chap6.html

        **example**:

            >>> from decida.Data import Data
            >>> d = Data()
            >>> d.read_sspar("spar.data")

        """
        #---------------------------------------------------------------------
        # get file name if not specified
        #---------------------------------------------------------------------
        if not file :
            type = "Cadence Spectre S-parameter File"
            file = tkFileDialog.askopenfilename(
                title="%s to read?" % (type),
                initialdir=os.getcwd(),
                defaultextension=".data",
                filetypes = (
                    ("sspar files", "*.data"),
                    ("sspar files", "*.sp*"),
                    ("all files", "*")
                )
            )
        if not file :
            return
        if not os.path.exists(file) :
            self.warning("%s \"%s\" doesn't exist" % (type, file))
            return
        #---------------------------------------------------------------------
        # read data lines from file
        #---------------------------------------------------------------------
        f = open(file, "r")
        cols = []
        data = []
        npts = 0

        mode = "title"
        ncol = 0
        rref = []
        datp = []
        varp = []
        varf = False
        cxvars = []
        for line in f :
            line = string.strip(line)
            if   line == "" :
                pass
            elif re.search("^;", line) :
                pass
            elif re.search("^reference", line) :
                mode = "reference"
            elif re.search("^format", line) :
                mode = "variables"
                varp = string.split(line)
                varp.pop(0)
                varf = True
            elif re.search("^[0-9-]", line) :
                if mode != "data" :
                    mode = "data"
                    datp = []
                    ncol = len(cols)
                line = re.sub("[,:]", " ", line)
                toks = string.split(line)
                datp.extend(toks)
                if len(datp) >= ncol :
                    npts += 1
                    data.extend(datp)
                    datp = []
            elif mode == "reference" :
                rref.append(line)
            elif mode == "variables" :           
                varp = string.split(line)
                varf = True
            if varf :
                varf = False
                for var in varp :
                    if re.search("^freq", var) :
                        cols.append("freq")
                    else :
                        m = re.search("^([^(]+)\((\w+),(\w+)\)$", var)
                        if m :
                            #--------------------------------------------------
                            # format specifications:
                            # (real,imag),
                            # (mag,deg), (mag,rad),
                            # (db,deg), (db,rad)
                            #--------------------------------------------------
                            root = m.group(1)
                            cx1  = m.group(2)
                            cx2  = m.group(3)
                            if cx2 == "deg" :
                                cx2 = "ph"
                            cx1 = string.upper(cx1) # real, mag, db
                            cx2 = string.upper(cx2) # imag, ph, rad
                            #--------------------------------------------------
                            # if port numbers are greater than
                            # 1 digit, keep the :, otherwise remove it
                            #--------------------------------------------------
                            m = re.search("^([a-zA-Z]+)(\d+):(\d+)", root)
                            if m :
                                p0 = m.group(1)
                                p1 = m.group(2)
                                p2 = m.group(3)
                                if len(p1) == 1 and len(p2) == 1 :
                                    root = "%s%s%s" % (p0, p1, p2)
                            cols.append("%s(%s)" % (cx1, root))
                            cols.append("%s(%s)" % (cx2, root))
                            cxvars.append(root)
        f.close()
        #---------------------------------------------------------------------
        # reformat data
        #---------------------------------------------------------------------
        ncol = len(cols)
        if ncol == 0 or npts == 0 :
            self.warning("problem reading %s \"%s\"" % (type, file))
            return
        try :
            a = numpy.zeros(npts*ncol, dtype="float64")
            for i, d in enumerate(data) :
                a[i] = string.atof(d)
        except :
            self.warning("problem reading %s \"%s\"" % (type, file))
            return
        self._data_array     = a.reshape(npts, ncol)
        self._data_col_names = cols
        self.title           = ""
        #---------------------------------------------------------------------
        # TBD:
        # * if real, imag, generate mag, db, ph
        # * if mag, db, rad, ph, generate real, imag 
        #---------------------------------------------------------------------
    #=========================================================================
    # METHOD: read_hjou
    # PURPOSE: read HSpice journal file
    #=========================================================================
    def __read_hjou(self, *args) :
        """ read HSpice journal file. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: read_tsv
    # PURPOSE: read tab separated value format file
    #=========================================================================
    def __read_tsv(self, *args) :
        """ read tab-separated value format file. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: read_varval
    # PURPOSE: read variable=value format file
    #=========================================================================
    def __read_varval(self, *args) :
        """ read variable=value format file. (not yet done)"""
        pass
    #=========================================================================
    # METHOD: read_vcd_csv
    # PURPOSE: read value-change-dump csv format file
    #=========================================================================
    def __read_vcd_csv(self, *args) :
        """ read value-change-dump csv format file. (not yet done)"""
        pass
