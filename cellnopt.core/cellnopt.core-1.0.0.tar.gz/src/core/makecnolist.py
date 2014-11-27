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
"""makecnolist module

Created by Thomas Cokelaer <cokelaer@ebi.ac.uk>
Copyright (c) 2011. GPL
"""
from __future__ import print_function
#from __future__ import unicode_literals

import numpy
import pylab

__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])


class MakeCNOListBase(object):
    """A base class to cnolist objects

    This object is used to create a structure based on MIDAS data.

    """
    def __init__(self, verbose=True):
        """

        Set the following attributes to empty list:

         * :attr:`namesSignals`
         * :attr:`namesCues`
         * :attr:`namesStimuli`
         * :attr:`namesNONC`
         * :attr:`namesInhibitors`
         * :attr:`namesInhibitorsShort`

        The attribute :attr:`namesInhibitorsShort` is read-only and simply returns
        the namesInhibitors without the letter 'i' at the end.

        """
        #: names of the signals nodes, if any
        self.namesSignals = []
        #: names of the cues nodes, if any
        self._namesCues = []
        #: names of the stimuli nodes, if any
        self._namesStimuli = []
        #: names of the NONC nodes, if any
        self.namesNONC = []
        #: names of the inhibitors nodes, if any
        self._namesInhibitors = []
        self.namesCompressed = []
        self._namesInhibitorsShort = []

        self.verbose = verbose

    def _getInhibitorsShort(self):
        return [name[0:-1] for name in self.namesInhibitors]
    namesInhibitorsShort = property(_getInhibitorsShort)


class MakeCNOList(MakeCNOListBase):
    """Create a CNOlist structure given MIDAS data

    Assume inhibitors from the MIDAS file finish with the letter **i**.

    :Example:

    ::

        from cinapps.core.cnograph import *
        m = MIDASReader(locate_data('MIDAS-Training-ToyModelMKM.csv'))
        cnolist = MakeCNOList(m)
        cnolist.nameCues
        cnolist.plot()

    :Attributes:

    Those inherited from :class:`MakeCNOListBase` :
        :attr:`~MakeCNOListBase.namesCues`,
        :attr:`~MakeCNOListBase.namesStimuli`,
        :attr:`~MakeCNOListBase.namesInhibitors`,
        :attr:`~MakeCNOListBase.namesSignals`

    And:

     * :attr:`timeSignals`     a vector of times
     * :attr:`valueCues`       a matrix of dimensions nConditions x nCues,
       with 0 or 1 if the cue is present or absent in the particular condition
     * :attr:`valueInhibitors` a matrix of dimensions nConditions x nInhibitors,
       with 0 or 1 if the inhibitor is present or absent in the particular condition
     * :attr:`valueStimuli`    of dimensions nConditions x nStimuli, with 0 or 1
        if the stimuli is present or absent in the particular condition
     * :attr:`valueSignals`    a list of the same length as timeSignals, each element
        containing a matrix of dimensions nConditions x nsignals, with the measurements.

    """
    def __init__(self, midas=None, verbose=True):
        """Constructor

        :param midas: a :class:`~cinapps.core.midas.MIDASReader` object

        """
        super(MakeCNOList, self).__init__(verbose=verbose)

        # some info from midas
        self._midas = midas
        self._midas_TRcol = midas.TRcol[:]
        self._midas_DVcol = midas.DVcol[:]
        self._midas_names = midas.names[:]
        self._midas_length = midas.dataMatrix.shape[0]


        # extract indices
        indexStimuli = [self.namesCues.index(name) for name in self.namesStimuli]

        # extract   indices. Note that in CNOR, the i is removed. We keep it
        #indexInhibitors = [self.namesCues.index(name[0:-1]) for name in self.namesInhibitors]

        # !! should use the names with the "i" chracter at the end in case
        # stimuli and inhibitor share the same name.
        cues = self.namesStimuli + self.namesInhibitors
        indexInhibitors = [cues.index(name) for name in self.namesInhibitors]

        # Need to cope with those specific cases
        #"if "NOCYTO" in self.namesCues:
        #    raise NotImplementedError
        #if "NOINHIB" in self.namesCues:
        #    raise NotImplementedError

        # Extract the names of the signals
        self.namesSignals = [midas.names[i].split(':')[1] for i in midas.DVcol]

        # Extract the time signals
        submatrix_signals = midas.dataMatrix[:,numpy.array(midas.DAcol)]
        #: timeSignals store the signals in a matrix
        self.timeSignals = list(numpy.unique(submatrix_signals))
        self.timepoints = list(numpy.unique(submatrix_signals))

        # Finally, the time
        #assert midas.dataMatrix.shape[0]%self.ntime ==0 , "shape of the midas matrix seems wrong. "

        t0 = 0
        t1 = self.nrow
        #: valueCues, a sub-matrix of the midas.dataMatrix to store TR columns only


        #We should extract the unique combinaisons and compute average over different replicates

        self.valueCues = midas.dataMatrix[t0:t1, numpy.array(midas.TRcol)]

        #: valueStimuli, a sub-matrix of the midas.dataMatrix to store stimuli
        self.valueStimuli = midas.dataMatrix[t0:t1, numpy.array(indexStimuli)]

        #: valueInhibitors, a sub-matrix of the midas.dataMatrix to store inhibitors
        try:
            self.valueInhibitors = midas.dataMatrix[t0:t1, numpy.array(indexInhibitors)]
        except:
            self.valueInhibitors = midas.dataMatrix[t0:t1, indexInhibitors]

        # finally, we get the valueSignals. Since, we do not know if a user has to enter
        # all data in the proper order, we must read each row, extract the times
        # and then fill the timeSignals. Not neat, but there is no clear
        # MIDAS format for now.

        # first, retrieve the data matrix shape from midas data and create the appropriate numpy matrix
        #: valueSignals
        self.valueSignals = numpy.array([0]*self.ndata , dtype=float).reshape(self.nrow, self.nspecies, self.ntime)
        # then, scan the data to fill the time matrix. first some aliases to the
        # column of interest
        DAcol = numpy.array(midas.DAcol)
        DVcol = numpy.array(midas.DVcol)

        count = 0

        for count, row in enumerate(midas.dataMatrix):
            time = row[DAcol]  # should contain a list of identical time. check ?
            time_index = self.timeSignals.index(time[0]) # index of this time
            data = row[DVcol] # data is a subrow corresponding to DVcol indices
            self.valueSignals[count%self.nrow, numpy.arange(0, self.nspecies), time_index] = data

        # restructure to have the same structure as in CNOR that is a list of matrices
        # instead of multidimensional array
        self.valueSignals = [self.valueSignals[:,:,i] for i in range(self.ntime)]

        # compute the residual errors stored in self.residualErrors
        #: store the residual errors :math:`\sum_{i,j} \left(x_{i,j}-x_{i,j}\right)^2`
        self._residualErrors = None

        #: fontsize used in the  plotting functions
        self.fontsize=12
        
    def factorise_time(self, indices, function):
        from numpy import array
        data = array(self.valueSignals)
        ntimes, nexp, nspecies = data.shape

        try:
            for i in indices:
                data[i]
        except IndexError:
            print("time indices don't seem to match your data")
            return

        if function == "max":
            # dirty loops to be replaced
            # loop over species:
            for i in range(0, nexp):
                for j in range(0, nspecies):
                    M = max([data[k,i,j] for k in indices])
                    data[indices[0],i,j] = M
                if len(indices)>1:
                    for k in indices[1:]:
                        data[k, i, j] = -1
            if len(indices)>1:
                data = numpy.delete(data, indices[1:], axis=0)
                self.timeSignals = [x for i,x in enumerate(self.timeSignals) if i not in indices[1:]]
                self.timepoints = self.timeSignals[:]
            self.valueSignals = data

        elif function == "min":
            raise NotImplementedError
        else:
            raise NotImplementedError

    def _get_namesInhibitors(self):
        names = [self._midas_names[i].split(':')[1] for i in self._midas_TRcol]
        names = [x for x in names if x[-1]=="i"]
        return names
    namesInhibitors = property(_get_namesInhibitors) 

    def _get_namesStimuli(self):
        names = [self._midas_names[i].split(':')[1] for i in self._midas_TRcol]
        names = [x for x in names if x[-1]!="i"]
        return names
    namesStimuli = property(_get_namesStimuli)
    
    def _get_namesCues(self):
        namesCues = [self._midas_names[i].split(':')[1] for i in self._midas_TRcol]
        namesCues = [x[0:-1] if x.endswith("i")==True else x for x in namesCues]
        self._namesCues = namesCues
        return self._namesCues
    namesCues = property(_get_namesCues, 
                         doc="Names of the Cues (Read only attributes)")

    def _get_nspecies(self):
        return len(self._midas_DVcol)
    nspecies = property(_get_nspecies)
       
    def _get_ntime(self):
        return len(self.timeSignals)
    ntime = property(_get_ntime)
    
    def _get_nrow(self):
        return int(self._midas_length/self.ntime)
    nrow = property(_get_nrow)
    
    def _get_ndata(self):
        return self.nspecies * self.nrow * self.ntime
    ndata = property(_get_ndata)


    def pcolor(self, time=1, **kargs):
        """

        :param int time: time index

        """
        assert time <= len(self.timeSignals)-1

        pylab.clf()
        pylab.pcolor(self.valueSignals[time],
            vmin=kargs.get('vmin',0),
            vmax=kargs.get('vmax', 1))
        pylab.title("Time %s" % self.timeSignals[time])
        pylab.ylabel("Experiments")
        xpos = pylab.arange(0, self.valueSignals[time].shape[1])+0.5
        pylab.xticks(xpos, [n.replace('_','\_') for n in self.namesSignals],rotation=60)
        pylab.colorbar()
        pylab.axis([0,self.valueSignals[time].shape[1], 0, self.valueSignals[time].shape[0]])


    def __str__(self):
        str_ = "nameCues\n"
        str_ += str(self.namesCues) + '\n\n'

        str_ += "namesStimuli\n"
        str_ += str(self.namesStimuli) + '\n\n'

        str_ += "namesInhibitors\n"
        str_ += str(self.namesInhibitors) + '\n\n'

        str_ += "namesSignals\n"
        str_ += str(self.namesSignals) + '\n\n'

        str_ += "timeSignals\n"
        str_ += str(self.timeSignals) + '\n\n'

        str_ += "valueCues\n"
        str_ += str(self.valueCues) + '\n\n'

        str_ += "valueInhibitors\n"
        str_ += str(self.valueInhibitors) + '\n\n'

        str_ += "valueStimuli\n"
        str_ += str(self.valueStimuli) + '\n\n'

        str_ += "valueSignals\n"
        for this in self.valueSignals:
            str_ += this.__str__() + '\n\n'

        return str_

    
    def plot_exp(self, t=1, sort_names=True):
        """Plot a colormap of the MIDAS data

        .. plot::
            :width: 50%
            :include-source:

            from cellnopt.core import *
            m = MIDASReader(cnodata('MD-ToyMMB.csv'))
            m.cnolist.plot_exp()

        .. todo:: grey color for the NAN. Need a special colormap ?
        .. todo:: fix the top label that are shifted
        """
    
        data = self.valueSignals[t]
        Nexp = data.shape[0]
        Nsti = len(self.namesStimuli)
        
        # some aliases
        signals = self.namesSignals
        
        # to store the labesls
        xlabels_bottom = []
        xlabels_top = []

        # get unique cues and stimuli combinaison sorted
        uniq_cues = sorted([list(x) for x in set(tuple(x) for x in self.valueCues)])
        uniq_stimuli = sorted([list(x) for x in set(tuple(x) for x in self.valueStimuli)])

        # and ordered indices
        mapping = [[list(y) for y in self.valueCues].index(x) for x in uniq_cues]    
        
        # rearrange the data at the requested time
        newdata = self.valueSignals[t][mapping]
        newdata = newdata.transpose()  # could remove and loop over Nexp first
        
        #loop over the data to remove NAN
        for i in range(0, len(signals)):
            for j in range(0, Nexp):
                datum = newdata[i,j]
                if pylab.isnan(datum):
                    newdata[i,j] = -1

        # build top and bottom labels using cues and stimuli/imhibitors
        for cues in uniq_cues:
            stim = cues[0:Nsti]
            inhs = cues[Nsti:]
                        
            # inhibitors labels
            if sum(inhs) == 0:
                xlabels_bottom.append("None")
            else:
                a = []
                for i, s in enumerate(inhs):
                    if s == 1:
                        a.append(str(self.namesInhibitorsShort[i]))
                xlabels_bottom.append("+".join(a))
            
            #top labels
            if sum(stim) == 0 and "None" not in xlabels_top:
                xlabels_top.append("None")
            else:
                a = []
                for i, s in enumerate(stim):
                    if s == 1:
                        a.append(str(self.namesStimuli[i]))
                if len(a) and "+".join(a) not in xlabels_top:
                    xlabels_top.append("+".join(a))
        
                
        # get the names and sorte  if needed, in which case rearrange the data
        names = self.namesSignals[:]
                
        if sort_names:
            sorted_indices_names = numpy.argsort(names)
            names.sort()
            newdata = newdata[sorted_indices_names,:]
            
        # reverse name because pcolor has its x=0y=0 in top left corner
        names.reverse()    
        names = [name.replace("_", "\_") for name in names]
        
        # the plotting itself
        pylab.clf()
        pylab.pcolor(numpy.flipud(newdata), edgecolors='black')
        
        print(xlabels_top)
        ticks = [[list(x) for x in self.valueStimuli].count(y) for y in uniq_stimuli]
        for this in numpy.cumsum(ticks):
            pylab.plot([this, this],[0,len(signals)], lw=4, color="grey")
        
        
        pylab.yticks(pylab.linspace(0.5, len(names)+0.5, len(names)+1), names)

        pylab.xticks(pylab.linspace(0.5, Nexp+.5, Nexp+1 ),
                     xlabels_bottom, rotation=90)

        pylab.ylim(0,len(signals))
        pylab.xlim(0,Nexp)
        a = pylab.gca()
        
        pylab.colorbar()
        pylab.hot()
        # now the top labels
        
        yy = a.twiny()
                
        ticks = numpy.array([[list(x) for x in self.valueStimuli].count(y) for y in uniq_stimuli])
        print(numpy.cumsum(ticks) - numpy.array(ticks)/2. )
        yy.set_xticks(numpy.cumsum(ticks) - ticks[0] + numpy.array(ticks)/2. )
        yy.set_xticklabels(xlabels_top)

        # bug in matplotlib, need to repring after twiny...?
        pylab.yticks(pylab.linspace(0.5, len(names)+0.5, len(names)+1), names)

        

    def _get_residualErrors(self):
        """Compute the residual errors at each time step

        :return: a dictionary with keys as time and values as residual errors

        
        This is a private method called in the constructor that po
        """
        residualErrors = {}
        for i, t in enumerate(self.timeSignals):
            if i != 0:
                data = self.valueSignals[i]
                diff = (numpy.round(data) - data)
                errors = numpy.square(diff)
                residualErrors[t] = numpy.nansum(errors)


        if self.verbose:
            for k, v in residualErrors.iteritems():
                print('Time %s : residual error is %s' % (k, v))
        return residualErrors
    residualErrors = property(_get_residualErrors, 
        doc="""Returns residual errors :math:`\sum (round(x)-x)^2` read-only""")    








