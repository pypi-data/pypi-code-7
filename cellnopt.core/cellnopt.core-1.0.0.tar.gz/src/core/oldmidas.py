# -*- python -*-
#
#  This file is part of the cinapps.tcell package
#
#  Copyright (c) 2012-2013 - EMBL-EBI
#
#  File author(s): Thomas Cokelaer (cokelaer@ebi.ac.uk)
#
#  Distributed under the GLPv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: www.cellnopt.org
#
##############################################################################
from __future__ import print_function
#from __future__ import unicode_literals
import types


from numpy import delete as numpy_delete
from numpy import genfromtxt as numpy_genfromtxt
import pylab
import numpy
import numpy as np
import pandas as pd

from cellnopt.core.makecnolist import MakeCNOList
from easydev import  Logging
from cellnopt.data import cnodata
from colormap import Colormap

__all__ = ["MultiMIDAS", "MIDASReader", "readMIDAS"]

def readMIDAS(self, filename, cellLine="CellLine",verbose=True):
    m = MIDASReader(filename, cellLine, verbose)
    return m




class DummyCNOlist(object):
    """a temporary class that should be removed"""
    def __init__(self):
        self.namesCues = []
        self.namesSignals = []
        self.namesStimuli = []
        self.namesInhibitors = []
        self.namesInhibitorsShort = []
        self.namesNONC = []
        self.valueCues = numpy.zeros((1,1))
        self.valueSignals = []
        self.valueStimuli = []
        self.valueInhibitors = []
        self.timepoints = []
        self.namesCompressed = []



class MIDAS(object):
    """What is it ?"""
    valid_codes = {
                   'ID':'identifier',
                   'TR':'stimuli/inhibitors',
                   'DA':'times',
                   'DV':'measurements'}

    ignore_codes = ['NOINHIB', 'NOCYTO', 'NOLIG', 'NO-CYTO', 'NO-INHIB', 'NO-LIG']

    def __init__(self, filename=None, verbose=False):
        """.. rubric:: Constructor

        :param str filename: the filename (including correct path)

        """
        self._header = []
        self._names = []
        self.verbose = verbose

        #: filename of the original data
        self.filename = filename

        self.cmap_scale=1
        self.fontsize=16
        self.logging = Logging("INFO")
        self._colormap = Colormap()


    # a readonly property to access the indices of data type (e.g., DA, TR, ...)
    def _get_col(self, prefix):
        known = ["TR", "DV", "DA", "ID"]
        if prefix == "unknown":
            return [i for i,x in enumerate(self.names) if x[0:2] not in known]

        elif prefix in known:
            return [i for i,x in enumerate(self.names) if x[0:2] == prefix]
    # The following syntax (property and lambda) is a trick to use a
    # property with argument (here 'DA' ,'TR', ...)
    DAcol = property(lambda s: s._get_col('DA'),
                     doc="return column indices referring to DA")
    DVcol = property(lambda s: s._get_col('DV'),
                     doc="return column indices referring to DV")
    TRcol = property(lambda s: s._get_col('TR'),
                     doc="return column indices referring to TR")
    IDcol = property(lambda s: s._get_col('ID'),
                     doc="return column indices referring to ID")

    def _get_nExps(self):
        try:
            return self.cnolist.valueCues.shape[0]
        except:
            return len(self.experiments)
    nExps = property(_get_nExps)




class MIDASReader(MIDAS):
    """Read a MIDAS file. See :ref:`midas`

    This object reads a MIDAS file that is a CSV file containing experimental
    data.

    .. doctest::

        >>> from cellnopt.core import MIDASReader, cnodata
        >>> m = MIDASReader(cnodata('MD-ToyMMB.csv'))


    The first line of the MIDAS file must be a header made of names that are stored in
    :attr:`~cellnopt.core.midas.MIDASReader.names`. Each name correspond to a column
    of the data that follows. Names must be of the form::

        XX:whatever

    where XX indicates the type of data measured. It must be one of DA, DV,
    TR. The name that follows the : sign should indicate a
    signals or cues.

    Then, the remaining data is scanned and rendered as a matrix array and
    stored in :attr:`dataMatrix`. However, the data structure to be used is
    the cnolist attribute.

    .. note:: The special column called **TR:CellLine** is ignored while creating the
        data Matrix. Similarly for TR:CellType, TR:NOINHIB and TR:NOCYTO.


    .. warning:: know issues. (1) m =  MIDASReader("share/data/MD-unnorm_exp.csv") does not work properly.
        only one combi of stimuli is read

    :References: [CellNOpt]_


    """

    # in some MIDAS files, these zords are used to tag special columns, which have
    # no meaning in cellnopt. So, we ignore them.
    celltype_codes = ['CellType', 'CellLine']

    def __init__(self, filename=None, verbose=True, celltype=None, **kargs):
        """.. rubric:: Constructor

        :param str filename: the filename (including correct path)
        :param str cellLine: a valid cellLine to be found in the file. Required only
            if there are at least 2 cellines in the MIDAS file. If there is only
            one cellLine, this parameter is ignored.
        :param bool verbose: prints informative messages
        :param kargs: optional arguments of numpy.genfromtxt


        Except from **names** and skip_header, all optional arguments
        accepted by numpy.genfromtxt can be provided as optional arguments.

        The **skip_header** cannot be used because MIDAS file has a header
        made of one line. The **names** argument of genfromtxt is therefore
        irrelevant.


        :attributes:

          * :attr:`names` names found in the header
          * :attr:`data`  a copy of the original data
          * :attr:`dataMatrix` the MIDAS data
          * :attr:`DAcol` indices of the DA columns
          * :attr:`TRcol` indices of the TR columns
          * :attr:`DVcol` indices of the DV columns
          * :attr:`nrows` and :attr:`ncols` the shape of :attr:`dataMatrix`
            (without cellLine and cellType).
          * :attr:`filename`
          * :attr:`verbose`


        .. doctest::

            >>> from cellnopt.core import MIDASReader, cnodata
            >>> m = MIDASReader(cnodata('MD-LiverDREAM.csv'))
            >>> data = m.dataMatrix
            >>> names = m.names # contains all columns names
            >>> m.nrows
            50
            >>> m.ncols
            22
            >>> coldata = m['DA:p38']

        .. todo:: DA:ALL  datamatrix seems to be the transpose matrix of cnor.datamatrix

        .. todo:: many different inputs. e.g sometimes header uses double quotes
            around names.
        """
        super(MIDASReader, self).__init__(filename)
        print("""Will be deprecated soon. Use XMIDAS instead""")

        #: a verbose option
        self.verbose = verbose
        self.celltype_user = celltype
        self.kargs = kargs.copy()



        self.cnolist = DummyCNOlist()

        if isinstance(filename, str):
            self.filename = filename
            self.readfile()
        elif filename == None:
            pass
        else: #could be a MIDAS instance from R ??
            import tempfile
            from cellnopt.wrapper import writeMIDAS
            fh = tempfile.NamedTemporaryFile(delete=False)
            fh.close()
            writeMIDAS(filename, fh.name, overwrite=True)
            self.filename = fh.name
            self.readfile()
            fh.delete = True
            fh.close()


        if filename:
            self.create_empty_simulation()

    def _get_names(self):
        return self._names
    names = property(fget=_get_names, doc="names Read-only attribute.")

    def _get_time(self):
        return self.cnolist.timepoints
    times = property(_get_time)

    def _get_nInhibitors(self):
        return len(self.namesInhibitors)
    nInhibitors = property(_get_nInhibitors)

    def _get_nStimuli(self):
        return len(self.namesStimuli)
    nStimuli = property(_get_nStimuli)

    def _get_nCues(self):
        return len(self.namesCues)
    nCues = property(_get_nCues)

    def _get_nSignals(self):
        return len(self.namesSignals)
    nSignals = property(_get_nSignals)


    # exp is not the proper name...
    def _get_exp(self):
        return self.cnolist.valueSignals
    exp = property(_get_exp)

    def _get_namesStimuli(self):
        return self.cnolist.namesStimuli
    namesStimuli = property(_get_namesStimuli)

    # use short name (without i)
    def _get_namesInhibitors(self):
        return self.cnolist.namesInhibitorsShort
    namesInhibitors = property(_get_namesInhibitors)

    def _get_namesSignals(self):
        return self.cnolist.namesSignals
    namesSignals = property(_get_namesSignals)

    def _getInhibitors(self):
        return numpy.array(self.cnolist.valueInhibitors)
    inhibitors = property(_getInhibitors)

    def _getStimuli(self):
        return numpy.array(self.cnolist.valueStimuli)
    stimuli = property(_getStimuli)

    def _get_ntimes(self):
        return len(self.exp)
    ntimes = property(_get_ntimes, doc="Returns number of time points (read-only)")

    def _get_names_cues(self):
        return self.cnolist.namesCues
    namesCues = property(_get_names_cues)


    def _readHeader(self):
        # For some unknown reason, genfromtxt remove the : in the header, so we need
        # to read the names first.
        f = open(self.filename, 'rU')        # open the file in read only mode 
        #03/10/2013 (luca)  added universal newline support. If not enabled,

        header = f.readline()               # read the first line
        f.close()                           # close the file

        header = header.rstrip('\n')       # remove the \n character
        header = header.rstrip('\r')     # remove the \r character if any

        colnames = [str(c) for c in header.split(",")] # split the names

        # sometimes, in MIDAS file, people code the names with quote. need to
        # remove them for consistency.
        colnames = [name.replace("\"", "").strip() for name in colnames]
        
        return colnames

    def _get_celltypes(self):
        # identify celltypes
        celltypes = {}
        _celltypes = dict([(x,i) for i,x in enumerate(self.names)
            if x.lower().endswith("cellline")
            or x.lower().endswith("celltype")])

        # check the format TR:<tag>:CellLine  where <tag> can be empty
        for celltype,v in _celltypes.iteritems():
            if celltype.count(":") != 2:
                raise ValueError("""MIDAS celltype (%s) has an invalid format.
    Should be TR:<tag>:CellLine""" % celltype)
            name = celltype.split(":")[1]
            name = name.strip()
            if len(name):
                celltypes[name] = v
            else:
                celltypes["unspecified"] = v

        return celltypes


    def readfile(self, filename=None):
        """The main function that reads the CSV file

        :param str filename: if provided, the attribute :attr:`filename` is
            overwritten with this argument. In all case, the :attr:`filename` is
            read to populate data attributes.

        The first column (cellLine) is ignored if there is only one cellLine.
        Otherwise, the :attr:`cellLine` must be provided as a selector. If you have

        .. note:: The special column with names NOINHIB and NOCYTO are ignored.
            You can add more columns with any identifiers (e.g.: EX:score)

        """
        # use the filename is provided
        if filename:
            self.filename = filename

        # read the header and extract the column names
        self._names = self._readHeader()

        # performs some checking on the found names
        self._name_validator()

        #!!! since we remove the CellLines at index zero, the indices
        # of other code (e.g, DA) starts at 1. This is identical to
        # R convention by pure chance.

        # read the data and remove the celllines columns
        kargs = self.kargs.copy()
        kargs['names'] = None
        kargs['skip_header'] = 1
        kargs['delimiter'] = ','

        # original data matrix is saved and not touched
        _data = numpy_genfromtxt(self.filename, **kargs)
        self._rawdata = _data.copy()

        # the dataMatrix stores data without cellline columns
        self.dataMatrix = _data.copy()

        # Read the celllines or celltype names.
        celltypes = self._get_celltypes()

        # Identify celltype name requested by the user and raise error if needed.
        if len(celltypes)>=2 and self.celltype_user == None:
            self.logging.error("You have more than 1 cellType in your data. You must provide a celltype name")
            self.logging.error("valid celltype names are %s " % celltypes.keys())
            raise ValueError
        elif len(celltypes)>=2 and self.celltype_user != None:
            if self.celltype_user not in celltypes.keys():
                raise ValueError("invalid celltype provided. Use one of %s" % celltypes.keys())
            self.celltypeName = self.celltype_user
        elif len(celltypes.keys())==1:
            # nothing to do if only one celltype in the data
            self.celltypeName = celltypes.keys()[0]
        else:
            self.celltypeName = "unspecified"

        # now clean up the data MAtrix to remove all columns corresponding to
        # the celltypes and all rows that do not correspond to celltypeName that
        # has been requested by the user

        if len(celltypes.keys()):
            # keep only rows matching the requested celltype
            indexCellType = celltypes[self.celltypeName]
            rowIndices = numpy.where(self.dataMatrix[:,indexCellType]!=1)
            self.dataMatrix = numpy_delete(self.dataMatrix, rowIndices, axis=0)

            # remove the cellline columns:
            colIndices = celltypes.values()
            self.dataMatrix = numpy_delete(self.dataMatrix, colIndices, axis=1)
            self._names = [name for i,name in enumerate(self._names) if i not in celltypes.values()] 
    
        # remove extra columns to ignore
        for code in self.ignore_codes:
            indices = [i for i,x in enumerate(self.names) if code in x]
            names = [x for i,x in enumerate(self.names) if code in x]
            self.dataMatrix = numpy_delete(self.dataMatrix, indices, axis=1)
            for name in names:
                self._names.remove(name)

        # finally, identify invalid/unknown prefixes to store them separetely
        indices = [i for i,x in enumerate(self.names) if x.split(":")[0] not in self.valid_codes.keys()]
        self.dataExtra = self.dataMatrix[:, indices]
        self.namesExtra = [self.names[i] for i in indices]
        self.dataMatrix = numpy_delete(self.dataMatrix, indices, axis=1)
        for name in self.namesExtra:
            self._names.remove(name)

        # perform some sanity checks
        self._validation()

        #: A CNOList object
        try:
            self._build_cnolist()
        except Exception, e:
            print(e)
            print("could not build cnolist")

    def _name_validator(self):
        """Check that the header is correct.

        1. name starts with TR, DA, DV
        2. names have at least one and at max 2 sign :

        """
        for i, name in enumerate(self.names):
            if name[0:2] not in self.valid_codes.keys():
                self.logging.warning("""Unusual header file: found column %s (%s)
not starting with one of %s""" % (i+1, name, self.valid_codes.keys()))

        for i, name in enumerate(self.names):
            if name.count(":") not in [1,2]:
                raise ValueError("""Header file not valid: found column %s (%s)
#with no : sign or more than 2.""" % (i+1, name))


    def _build_cnolist(self):
        self.cnolist = MakeCNOList(self)


    # a readonly property to acces the number of rows
    def _get_nrows(self):
        return self.dataMatrix.shape[0]
    nrows = property(_get_nrows,
                     doc="return the number of rows in :attr:`dataMatrix`")

    # a readonly property to acces the number of columns
    def _get_ncols(self):
        return self.dataMatrix.shape[1]
    ncols = property(_get_ncols,
                     doc="return the number of colums in :attr:`dataMatrix`")


    def _validation(self):
        """Sanity checks to be completed when more information is provided


        """
        # number of DA must equal number of DV
        if len(self.DAcol) != len(self.DVcol):
            if len(self.DAcol) == 1:
                if self.names[self.DAcol[0]] != "DA:ALL":
                    raise ValueError('DA column is not DA:ALL and is not same as DV columns')
                else:
                    pass
            else:
                raise ValueError("Number of DA columns does not match nuber of DV columns")

    def __getitem__(self, name):
        """Return column corresponding to a given name

        :param str name: a valid name that can be found in :attr:`names`

        This is an alias to m.dataMatrix[:,indices to the column of interest].

        ::

            m['TR:EGF'] == m.dataMatrix[:,m.names.index('TR:EGF')-1]

        """
        if name in self.names:
            index = self.names.index(name)# be careful will celllines
            return self.dataMatrix[:,index]
        elif name in self.namesExtra:
            index = self.namesExtra.index(name)
            return self.dataExtra[:,index]
        else:
            raise ValueError("Invalid name. Valid keys are %s" % self.names)

    def remove_column(self, name):
        """Delete a name from the list of names and update dataMatrix

        :param str name: data to delete

        ::

            m.remove('TR:EGF')
        """

        if name in self.names:
            if self.verbose:
                print('delete ', name)
            if name.startswith('DA') or name.startswith('DV'):
                print("WARNING: if you delete a DA:specy, you must also delete DV:specy")
            i = self.names.index(name) - 1  # because of the cellline ?
            self.dataMatrix = numpy_delete(self.dataMatrix, i, axis=1)
            self.names.remove(name)
        else:
            raise ValueError("invalid name. Valid names are %s" % self.names)

        # need to rebuild the cnolist
        self._build_cnolist()

    def __str__(self):
        msg = "Your data set comprises\n"
        msg += "    %s conditions (i.e. combinations of time point and treatment)\n" % self.nrows

        msg += " %s cues:" % len(self.namesCues)
        for name in self.namesCues:
            msg += " " + name
        msg +="\n"

        msg += " %s inhibitors:" % len(self.namesInhibitors)
        for name in self.namesInhibitors:
            msg += " " + name
        msg +="\n"

        msg += " %s stimuli:" % len(self.namesStimuli)
        for name in self.namesStimuli:
            msg += " " + name
        msg +="\n"

        msg += " %s time points:" % len(self.times)
        for name in self.times:
            msg += " " + str(name)
        msg +="\n"

        msg += " %s signals:" % len(self.namesSignals)
        for name in self.namesSignals:
            msg += " " + str(name)
        msg +="\n"

        return msg


    def factorise_time(self, indices, function):
        self.cnolist.factorise_time(indices, function)

    def save(self, filename):
        """Save the midas data into a file

        once you have added noise with :meth:`add_noise`, call this function to
        save the midas data into a file.

        :param str filename: the output filename

        """
        # using cnolist data or this midas data
        # for now, let us use the cnolist that seems simpler.

        f = open(filename, "w")
        # first; the header
        header =  ["TR:" + self.celltypeName + ":CellLine"]
        header += self.names
        header = ",".join(header)
        f.write(header+"\n")

        for itime, time in enumerate(self.cnolist.timeSignals):
            for row in range(0, self.cnolist.valueCues.shape[0]):
                data = ["1"] # for the cellline
                for x in list(self.cnolist.valueCues[row]):
                    try:
                        data += [int(x)]
                    except:
                        data += [""]

                data += [int(time)] * len(self.DAcol)
                data += list(self.cnolist.valueSignals[itime][row])
                f.write(",".join([str(x) for x in data])+"\n")

        #m.cnolist.valueSignals
        f.close()

    def get_diff(self, sim, norm="squared"):
        diff = numpy.zeros((self.nExps, self.nSignals)) # +1 to write the species
        exp = numpy.array(self.cnolist.valueSignals)

        if norm == "square":
            diff = numpy.mean(abs(sim - exp)**2, axis=0)
        else:
            diff = numpy.mean(abs(sim - exp), axis=0)

        return diff

    def create_empty_simulation(self):
        self.sim = numpy.array([numpy.zeros(self.exp[i].shape) for i in range(0,len(self.times))])

    def create_random_simulation(self):
        self.sim = numpy.array([numpy.random.uniform(size=self.exp[i].shape) for i in range(0,len(self.times))])

    def plotMSEs(self, cmap="heat", inverse=True, N=10, norm="squared",
        rotation=90,margin=0.05, colorbar=True, fontsize=12, mode="trend", **kargs):
        """plot MSE errors and layout


        .. plot::
            :width: 80%
            :include-source:

            >>> from cellnopt.core import *
            >>> m = midas.MIDASReader(cnodata("MD-ToyPB.csv"));
            >>> m.plotMSEs()

        .. todo:: error bars

        .. todo:: dynamic fontsize in the signal names ?

        """
        self.fontsize = fontsize
      
        if cmap == "heat":
            cmap = self._colormap.get_cmap_heat()
        elif cmap == "green":
            cmap = self._colormap.get_cmap_heat()

        diffs = self.get_diff(self.sim, norm=norm)

        pylab.clf();

        bW = 0.1
        cH = 0.1

        if len(self.namesInhibitors)>0:
            bbW = 0.1
        else:
            bbW = 0

        aH = 1-cH-4*margin
        aW = 1-bW-5*margin - bbW

        # MAIN subplot with signals
        a = pylab.axes([margin, 2*margin, aW, aH])
        M = numpy.nanmax(diffs) # figure out the maximum individual MSE
        m = numpy.nanmin(diffs) # figure out the minimum individual MSE
        vmax= max(1, M)       # if M below 1, set the max to 1 otherwise to M
        #if m == 0:
        vmin = 0
        #else:
        #    vmin = min(-1, m)

        #print(vmin, vmax)

        if mode == "mse":
            pylab.pcolor(pylab.flipud(diffs)**self.cmap_scale, cmap=cmap, vmin=vmin, vmax=vmax, edgecolors='k');
        elif mode == "trend":
            pylab.pcolor(pylab.flipud(diffs*0), cmap=cmap, edgecolors='k');

        a.set_yticks([],[])
        pylab.axis([0, diffs.shape[1], 0, diffs.shape[0]])

        # the stimuli
        b = pylab.axes([margin*2+aW, 2*margin, bW, aH])
        stimuli = numpy.where(numpy.isnan(self.stimuli)==False, self.stimuli, 0.5)

        pylab.pcolor(1-pylab.flipud(stimuli), edgecolors='gray', cmap='gray',vmin=0,vmax=1);
        b.set_yticks([],[])
        b.set_xticks([i+.5 for i,x in enumerate(self.namesStimuli)])
        b.set_xticklabels(self.namesStimuli, rotation=rotation)
        pylab.axis([0,self.stimuli.shape[1], 0, self.stimuli.shape[0]])

        # the inhibitors
        if len(self.namesInhibitors)>0:
            bb = pylab.axes([margin*5+aW, 2*margin, bbW, aH])
            inhibitors = numpy.where(numpy.isnan(self.inhibitors)==False, self.inhibitors, 0.5)
            pylab.pcolor(1-pylab.flipud(inhibitors), edgecolors='gray', cmap='gray',vmin=0,vmax=1);
            bb.set_yticks([],[])
            bb.set_xticks([i+.5 for i,x in enumerate(self.namesInhibitors)])
            bb.set_xticklabels(self.namesInhibitors, rotation=rotation)
            pylab.axis([0,self.inhibitors.shape[1], 0, self.inhibitors.shape[0]])

        # TOP area with names
        c = pylab.axes([margin, margin*3+aH, aW, cH])
        pylab.pcolor(1-numpy.zeros((1, self.nSignals)), edgecolors='b', cmap='gray',
               vmax=1, vmin=0);
        c.set_xticks([],[])
        c.set_yticks([],[])
        for i, signal in enumerate([x.replace("_","\_") for x in self.namesSignals]):
            pylab.text(i+.5,0.5, signal, horizontalalignment='center', color='blue',
                verticalalignment='center', fontsize=self.fontsize)

        d = pylab.axes([margin*2+aW, margin*3+aH, bW, cH])
        pylab.text(0.5,0.5, "Stimuli", color="blue", horizontalalignment="center",
            verticalalignment="center", fontsize=self.fontsize)
        #pcolor(1-numpy.zeros((1, 1)), edgecolors='b', cmap='gray', vmax=1, vmin=0);
        d.set_xticks([],[])
        d.set_yticks([],[])

        if len(self.namesInhibitors)>0:
            dd = pylab.axes([margin*5+aW, margin*3+aH, bbW, cH])
            pylab.text(0.5,0.5, "Inhibitors", color="blue", horizontalalignment="center",
                verticalalignment="center", fontsize=self.fontsize)
            #pcolor(1-numpy.zeros((1, 1)), edgecolors='b', cmap='gray', vmax=1, vmin=0);
            dd.set_xticks([],[])
            dd.set_yticks([],[])

        #colorbar
        # we build our own colorbar to place it on the RHS
        if colorbar and mode=="mse":
            e = pylab.axes([margin*3.5+aW+bW+bbW, 2*margin, margin/2, aH])
            cbar = inspace(0, 1, N)
            indices = [int(x) for x in cbar**self.cmap_ecale*(N-1)]

            cbar = [cbar[i] for i in indices]

            pylab.pcolor(numpy.array([cbar, cbar]).transpose(), cmap=cmap, vmin=0., vmax=1);
            #d.set_xticks([],[])
            e.yaxis.tick_right()
            #e.yaxis.xticks([0,1][0,1])
            # todo: why is it normalised by 20?


            ticks = numpy.array(e.get_yticks())
            M = max(ticks)
            indices = [int(N*x) for x in ticks**self.cmap_scale/(M**self.cmap_scale)]
            #print(indices)
            e.set_yticks(indices)
            if vmax == 1:
                e.set_yticklabels(numpy.array(indices)/float(N))
            else:
                e.set_yticklabels([int(x) for x in numpy.array(indices)/float(N)*vmax])

            e.set_xticks([],[])

        pylab.sca(a)

    def _get_xtlabels(self, logx=False):
        """build the time labels vector

        The vector is [t0,tmid,t0,tmid,...t0,tmid,tend]

        """
        times = numpy.array(self.times)
        #if logx == False:
        #    times = times/max(times)
        t0 = times[0]
        t2 = times[-1]

        #if len(times) > 2:
        xtlabels = [int(t0),int((t2-t0)/2)] * self.nSignals + [int(t2)]
        #else:
        #    xtlabels = [t0,t2] * self.nSignals
        return xtlabels

    def plotExp(self, markersize=3, logx=False, color="black", **kargs):
        """plot experimental curves

        .. plot::
            :width: 80%
            :include-source:

            >>> from cellnopt.core import *
            >>> m = midas.MIDASReader(cnodata("MD-ToyPB.csv"));
            >>> m.plotMSEs()
            >>> m.plotExp()

        """
        from pylab import  plot, gca, mod
        times = numpy.array(self.times)
        mode = kargs.get("mode", "trend")
        if logx == False:
            # a tick at x = 0, 0.5 in each box (size of 1) + last x=1 in last box
            xt = pylab.linspace(0, self.nSignals, self.nSignals*2+1)
            times = times/max(times)
            xtlabels = self._get_xtlabels(logx=True)
        else:
            #m = min(times)
            M = float(max(times))
            #mid = m + (M-m)/2.
            xtlin = pylab.linspace(0, self.nSignals, self.nSignals*2+1)
            xt = [int(x)+pylab.log10(1+mod(x,1)*M)/pylab.log10(1+M) for i,x in enumerate(xtlin)]
            xtlabels = self._get_xtlabels()
            times = pylab.log10(1+times)/max(pylab.log10(1+times))
        #for isim, sim in enumerate(self.sim):
        vMax = numpy.nanmax(self.exp)
        norm = numpy.trapz([1]*len(self.times), self.times)

        ts = TypicalTimeSeries(self.times)

        for i in range(0, self.nExps):
            for j in range(0, self.nSignals):
                # divide data by 1.1 to see results close to 1.
                y = numpy.array([x[i,j] for x in self.exp])/vMax/1.05
                if mode == "trend":
                    alpha = np.trapz(y, self.times) / norm
                    try:
                        color = ts.get_bestfit_color(y)
                    except:
                        color="white"
                    if color == "white":
                        colorc = "k"
                    else:
                        colorc=color
                    plot(times+j, y+self.nExps-i-1 , 'k-o', markersize=markersize, 
                        color=colorc)

                    #if y[0]>1.05*y[-1]:
                    #    color = "green"
                    #elif y[0]<y[-1]/1.05:
                    #    color = "red"
                    #else:
                    #    color = "black"
                    pylab.fill_between(times+j, y+self.nExps-1-i , self.nExps-1-i, alpha=alpha,
                        color=color)
                else:
                    plot(times+j, y+self.nExps-i-1 , 'k-o', markersize=markersize, 
                        color="k")


                #    plot(times+j, sim[i,j]/1.05+(self.nExps-i-1), 'b--o', markersize=markersize)
        gca().set_xticklabels(xtlabels)
        gca().set_xticks(xt)


    def plotSim(self, markersize=3, logx=False):
        """plot experimental curves

        .. plot::
            :width: 80%
            :include-source:

            >>> from cellnopt.core import *
            >>> m = midas.MIDASReader(cnodata("MD-ToyPB.csv"));
            >>> m.plotMSEs()
            >>> m.plotExp()
            >>> m.plotSim()

        """
        from pylab import log10, gca, mod
        times = numpy.array(self.times)
        if logx == False:
            # a tick at x = 0, 0.5 in each box (size of 1) + last x=1 in last box
            xt = pylab.linspace(0, self.nSignals, self.nSignals*2+1)
            times = times/max(times)
            xtlabels = self._get_xtlabels()
        else:
            #m = min(times)
            M = float(max(times))
            #mid = m + (M-m)/2.
            xtlin = pylab.linspace(0, self.nSignals, self.nSignals*2+1)
            xt = [int(x)+pylab.log10(1+mod(x,1)*M)/pylab.log10(1+M) for i,x in enumerate(xtlin)]
            xtlabels = self._get_xtlabels()
            times = pylab.log10(1+times)/max(pylab.log10(1+times))
        #for isim, sim in enumerate(self.sim):
        for i in range(0, self.nExps):
            for j in range(0, self.nSignals):
                # divide data by 1.1 to see results close to 1.
                pylab.plot(times+j, numpy.array([x[i,j] for x in self.sim])/1.05+(self.nExps-i-1), 'b--', markersize=markersize)
                #    pylab.plot(times+j, sim[i,j]/1.05+(self.nExps-i-1), 'b--o', markersize=markersize)
        gca().set_xticklabels(xtlabels)
        gca().set_xticks(xt)

    def plot(self, **kargs):
        mode = kargs.get("mode", "trend")
        kargs['mode'] = mode
        self.plotMSEs(**kargs)
        self.plotExp(**kargs)


    def export2CNOGraph(self):
        """Create a dummy CNOGraph with a "dummy" graph topology based on the MIDAS content.

        Creates a CNOGRaph instance to save the midas file as an attribute.
        Then, species, stimuli and inhibitors are added as nodes and a random
        set of edges is added using a random degreee distribution based on a
        gamma distribution

        """
        from cellnopt.core import CNOGraph
        c = CNOGraph()
        for n in self.namesSignals:
            c.add_node(n)
            c._signals.append(n)
        for n in self.namesStimuli:
            c.add_node(n)
            c._stimuli.append(n)
        for n in self.namesInhibitors:
            c.add_node(n)
            c._inhibitors.append(n)
        c.midas = self

        # create random edges with degree distribution following a gamma with
        # (7,05) parameter ( EGfr_ERb model)
        import networkx as nx
        N = len(c)
        # sum of the degrees must be even
        degrees = [int(numpy.random.gamma(7,0.5)) for i in range(0, N)]
        counter = 0
        while sum(degrees)%2 != 0 and counter<20:
            degrees = [int(numpy.random.gamma(7,0.5)) for i in range(0, N)]
            counter += 1
        cr = nx.configuration_model([x for x in degrees])
        nodes = c.nodes()
        for node in nodes:
            for node2_index in cr.edge[i].keys():
                if node != nodes[node2_index]:
                    c.add_edge(node, nodes[node2_index], link="+")

        return c

    def cut_by_time_index(self, index):
        
        if index > self.ntimes-1:
            msg = "index %s is not a valid index" % index
            msg += "It must be less than %s (size of 'time' attribute)" % str(self.ntimes-1)
            msg += "Be aware than Python convention is used for indices: starts at 0"
            raise ValueError(msg)
        self._remove_time_index(index)

    def cut_by_time_value(self, value):
        if value not in self.times:
            msg = "value %s is not a valid time" % value
            msg += "Valid times can be found in the attribute 'times'"
            raise ValueError(msg)
        index = self.times.index(value)
        self._remove_time_index(index)

    def _remove_time_index(self, index):
        print(index)
        del self.exp[index]
        #sim is not a list but a pure numpy array so no del available:
        self.sim = self.sim[[x for x in range(0, len(self.sim)) if x!=index],:,:]
        del self.cnolist.timepoints[index]
        del self.cnolist.timeSignals[index]
        #del self.cnolist.valueSignals[index]


class MIDASRandomiser(object):
    """Randomisation tools for MIDAS data structure

    .. plot::
        :include-source:
        :width: 50%

        from cellnopt.core import *
        m = MIDASReader(cnodata("MD-ToyPB.csv"))
        m2 = MIDASRandomiser(m)
        m2.midas.plot()
        m2.add_noise(dynamic_range=10)
        m2.midas.plotExp(color="green")

    """
    def __init__(self, midas, verbose=False):
        print("""Will be deprecate soon. Do not use. Use XMIDAS and its methods (e.g., add_uniform_distributed_noise""")
        if isinstance(midas, str):
            self.midas = MIDASReader(midas)
        else:
            if isinstance(midas, MIDASReader):
                #check the type of midas input file
                import copy
                self.midas = copy.deepcopy(midas)
            else:
                raise TypeError("midas argument must be a filename or output of MIDASReader")

        self.times = self.midas.cnolist.timeSignals[:]
        self.dimensions = self.midas.cnolist.valueSignals[1].shape

    def randomize(self):
        """Fill all data withe random values from uniform distribution"""
        for i, time in enumerate(self.times[1:]):
            # must loop over times to fill them with random data
            rdata = numpy.random.uniform(0,1,self.dimensions[0]*self.dimensions[1]).reshape(self.dimensions)
            self.midas.cnolist.valueSignals[i+1] = rdata.copy()

    def add_noise(self, noise='uniform', dynamic_range=1):
        """add uniform noise to the data


        :param str noise: uniform only is implemented so far
        :param float dynamic_range: added uniform noise is between -0.05 and 0.05
            you can change the min/max values by multiplying by dnamic range (default is 1)


        .. todo:: gaussian noise
        """
        for i, time in enumerate(self.times[1:]):
            # must loop over times to fill them with random data
            rdata = numpy.random.uniform(-.05,.05,self.dimensions[0]*self.dimensions[1]).reshape(self.dimensions)
            self.midas.cnolist.valueSignals[i+1] += rdata.copy()*float(dynamic_range)

        for i, time in enumerate(self.times[1:]):
            for j in range(0, self.dimensions[0]):
                for k in range(0, self.dimensions[1]):
                    if self.midas.cnolist.valueSignals[i+1][j,k] >1:
                        self.midas.cnolist.valueSignals[i+1][j,k] = 1
                    if self.midas.cnolist.valueSignals[i+1][j,k] <0:
                        self.midas.cnolist.valueSignals[i+1][j,k] = 0

        # cannot be less than  wero or greater than 1
        #for i in enumerate
        #    self.midas.cnolist.valueSignals[i+1] += rdata.copy()

    def __eq__(self, other):
        if (self.dataMatrix==other.dataMatrix).any() == False:
            return False
        if self.times != other.times:
            return False
        if (self.cnolist.valueCues == m2.cnolist.valueCues).any() == False:
            return False

        return True




# to be included somewhere
def _histogram_timepoints( filename, w=0.02):
    """

    todo : extract the N value automatically and loop over time
    """
    m = MIDASReader(filename)

    N = 11
    res1 = pylab.hist(m.dataMatrix[1,N:])
    bins = res1[1]
    res2 = pylab.hist(m.dataMatrix[2,N:], bins)
    res3 = pylab.hist(m.dataMatrix[3,N:], bins)
    res4 = pylab.hist(m.dataMatrix[4,N:], bins)
    res5 = pylab.hist(m.dataMatrix[5,N:], bins)


    pylab.bar(bins[0:-2],res1[0], width=w, label="1min")
    pylab.bar(bins[0:-2] + w, res2[0], width=w, color='red', label="5min")
    pylab.bar(bins[0:-2] + 2*w, res3[0], width=w, color='green', label="10min")
    pylab.bar(bins[0:-2] + 3*w, res4[0], width=w, color='yellow',label="15min")
    pylab.bar(bins[0:-2] + 4*w, res5[0], width=w, color='grey',label="30min");

    pylab.legend()
    pylab.grid()
    pylab.title("Distribution of the data function of time")
    pylab.ylabel("\#")
    pylab.xlabel("data values")


class MultiMIDAS(object):
    """Data structure to store multiple instances of MIDAS files


    You can read a MIDAS file that contains several cell lines:
    and acces to the midas files usig their cell line name

    .. doctest::

        >>> mm = MultiMIDAS(cnodata("EGFR-ErbB_PCB2009.csv"))
        >>> mm.cellLines
        ['HepG2', 'PriHu']
        >>> mm["HepG2"].namesCues
        ['TGFa', 'MEK12', 'p38', 'PI3K', 'mTORrap', 'GSK3', 'JNK']

    where the list of cell line names is available in the :attr:`cellLines`
    attribute.

    Or you can start from an empty list and add instance later on using :meth:`addMIDAS`
    method. 

    """
    def __init__(self, filename=None):
        """.. rubric:: constructor

        :param str filename: a valid MIDAS file (optional)

        """
        self._midasList = []
        self._names = []
        if filename:
            self.readMIDAS(filename)

    def addMIDAS(self, midas):
        """Add an existing MIDAS instance to the list of MIDAS instances

        .. doctest::

            >>> from cellnopt.core import *
            >>> m = MIDASReader(cnodata("MD-ToyPB.csv"))
            >>> mm = MultiMIDAS()
            >>> mm.addMIDAS(m)

        """
        if midas.celltypeName not in self._names:
            self._midasList.append(midas)
            self._names.append(midas.celltypeName)
        else:
            raise ValueError("midsa with same celltype already in the list")

    def readMIDAS(self, filename):
        """read MIDAS file and extract individual cellType/cellLine

        This function reads the MIDAS and identifies the cellLines. Then, it
        creates a MIDAS instance for each cellLines and add the MIDAS instance to the
        :attr:`_midasList`. The MIDAS file can then be retrieved using their
        cellLine name, which list is stored in :attr:`cellLines`.

        :param str filename: a valid MIDAS file containing any number of cellLines.




        """
        m = MIDASReader()
        m.filename = filename
        m._names = m._readHeader()
        celltypes = m._get_celltypes()
        if len(celltypes) <= 1:
            m = MIDASReader(filename)
            self.addMIDAS(m)
        else:
            for name in celltypes.keys():
                m = MIDASReader(filename, celltype=name)
                self.addMIDAS(m)

    def _get_cellLines(self):
        names = [x.celltypeName for x in self._midasList]
        return names
    cellLines = property(_get_cellLines, 
        doc="return names of all cell lines, which are the MIDAS instance identifier ")

    def __getitem__(self, name):
        index = self.cellLines.index(name)
        return self._midasList[index]

    def plot(self):
        """Call plot() method for each MIDAS instances in different figures

        More sophisticated plots to easily compare cellLines could be
        implemented.

        """
        for i,m in enumerate(self._midasList):
            from pylab import figure, clf
            figure(i+1)
            clf()
            m.plot()





class TypicalTimeSeries(object):
    """Utility that figures out the trend of a time series 

    Returns color similar to what is contained in DataRail.


    .. todo:: must deal with NA


    """
    def __init__(self, times=None):
        self._times = times  # ref do not change
    def _get_times(self):
        return self._times
    times = property(_get_times)

    def transient(self, x=None):
        """

        m = MIDASReader(...)
        y = transient(m.times)
        x = m.times
        plot(x,y)

        returns normqlised vector
        """
        if x == None:
            x = self.times
        M = max(x)
        v = np.array([(M-y)/(M/2.) if y>=M/2. else y/(M/2.) for y in x])
        return self._normed(v)

    def constant(self, x=0):
        v = np.array([x] * len(self.times))
        v = self._normed(v)
        return v

    def _normed(self, v):
        sumsq = np.sqrt(sum([this**2 for this in v]))
        return v/sumsq

    def earlier(self, x=None, n=3., N=4.):
        if x == None:
            x = self.times
        M = max(x)
        v = np.array([(M-y)/(n*M/N) if y>=M/N else y/(M/N) for y in x])
        return self._normed(v)

    def sustained(self, x=None, L=0.5):
        if x == None:
            x = self.times
        M = max(x)
        m = L * M
        v = np.array([y if y<m else m for y in x])
        return self._normed(v)

    def inverse_sustained(self, x=None, L=0.5):
        if x == None:
            x = self.times
        M = max(x)
        m = L * M
        v = np.array([(M-y) if y < m else M-m for y in x])
        return self._normed(v)


    def later(self, x=None, L=0.5):
        if x == None:
            x = self.times
        M = max(x)
        m = L * M
        v = np.array([0 if y<m else y-m for y in x])
        return self._normed(v)

    def _correlate(self, a, b):
        a = self._normed(a)
        b = self._normed(b)
        return np.correlate(a,b) 

    def _get_correlation(self, a):
        correlation = {}
        correlation['later'] = self._correlate(a, self.later())
        correlation['earlier'] = self._correlate(a, self.earlier())
        correlation['earlier2'] = self._correlate(a, self.earlier(n=1,N=10))
        correlation['transient'] = self._correlate(a, self.transient())
        correlation['constant_half'] = self._correlate(a, self.constant(0.5))
        correlation['constant_unity'] = self._correlate(a, self.constant(1))
        correlation['sustained'] = self._correlate(a, self.sustained(L=.5))
        correlation['inverse_sustained'] = self._correlate(a, self.inverse_sustained(L=.5))

        return correlation

    def plot(self, data):
        corrs = self._get_correlation(data)
        clf()
        pylab.plot(self.times, self._normed(data), label="data", lw=2, ls="--")
        # transient
        pylab.plot(self.times, self.transient(), 'o-', label="transient " + str(corrs['transient']))
        # earlier
        pylab.plot(self.times, self.earlier(), 'o-', label="earlier " + str(corrs['earlier']))
        pylab.plot(self.times, self.earlier(n=1, N=10), 'o-', label="earlier2 " + str(corrs['earlier2']))
        # later
        pylab.plot(self.times, self.later(), 'o-', label="later " + str(corrs['later']))
        # constant
        pylab.plot(self.times, self.constant(.5), 'o-', label="constant " + str(corrs['constant_half']))
        # sustained
        pylab.plot(self.times, self.sustained(L=.5), 'o-', label="sustained" + str(corrs['sustained']))
        pylab.plot(self.times, self.inverse_sustained(L=.5), 'o-', label="inv sustained" + str(corrs['inverse_sustained']))
        pylab.legend()

    def get_bestfit(self, data):
        corrs = self._get_correlation(data)
        keys,values = (corrs.keys(), corrs.values())
        M  = max(values)
        return keys[np.argmax(values)]

    def get_bestfit_color(self, data):
        corrs = self._get_correlation(data)
        keys,values = (corrs.keys(), corrs.values())
        M  = max(values)
        res = keys[np.argmax(values)]
        
        if "constant" in res:
            return "black"
        elif "later" in res:
            return "red"
        elif "transient" in res:
            return "yellow"
        elif "earlier" in res:
            return "purple"
        elif "sustained" in res:
            return "green"
        else:
            return "white"


