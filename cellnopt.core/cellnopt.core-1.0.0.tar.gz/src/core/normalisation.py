# -*- python -*-
#
#  This file is part of cellnopt.core software
#
#  Copyright (c) 2011-2013 - EBI-EMBL
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: www.cellnopt.org
#
##############################################################################

# cannot do from cellnopt.core import * ???
import midas
from oldmidas import MIDASReader
import easydev
#from cnograph import CNOGraph
import numpy as np

__all__ = ["NormaliseMIDAS", "XMIDASNormalise"]


class NormaliseMIDASBase(object):
    def __init__(self, mode="time", verbose=True, saturation=np.inf, 
                 detection=0., EC50noise=0., EC50data=0.5, HillCoeff=2.,
                changeThreshold=0.):
        
        # read-write attributes
        self.verbose = verbose
        self.mode = mode
        self.saturation = saturation
        self.EC50noise = EC50noise
        self.EC50data = EC50data
        self.HillCoeff = HillCoeff
        self.changeThreshold = changeThreshold
        self.detection = detection

    def _get_mode(self):
        return self._mode
    def _set_mode(self, mode):
        easydev.check_param_in_list(mode, ["time", "control"])
        self._mode = mode
    mode = property(_get_mode, _set_mode, doc="todo")

    def _get_saturation(self):
        return self._saturation
    def _set_saturation(self, saturation):
        if isinstance(saturation, (int, long, float)):
            self._saturation = saturation
        else:
            raise TypeError("saturation argument must be a number")
    saturation = property(_get_saturation, _set_saturation, 
        doc="saturation above which measurement are ignored")

    def _get_detection(self):
        return self._detection
    def _set_detection(self, detection):
        if isinstance(detection, (int, long, float)):
            self._detection = detection
        else:
            raise TypeError("detection argument must be a number")
    detection = property(_get_detection, _set_detection, 
        doc="detection above which measurement are ignored")

    def _get_EC50noise(self):
        return self._EC50noise
    def _set_EC50noise(self, EC50noise):
        if isinstance(EC50noise, (int, long, float)):
            self._EC50noise = EC50noise
        else:
            raise TypeError("EC50noise argument must be a number")
    EC50noise = property(_get_EC50noise, _set_EC50noise, doc="todo")

    def _get_EC50data(self):
        return self._EC50data
    def _set_EC50data(self, EC50data):
        if isinstance(EC50data, (int, long, float)):
            self._EC50data = EC50data
        else:
            raise TypeError("EC50data argument must be a number")
    EC50data = property(_get_EC50data, _set_EC50data, doc="todo")

    def _get_changeThreshold(self):
        return self._changeThreshold
    def _set_changeThreshold(self, changeThreshold):
        #if isinstance(changeThreshold, (int, long, float)):
        self._changeThreshold = changeThreshold
        #else:
        #    raise TypeError("changeThreshold argument must be a number")
    changeThreshold = property(_get_changeThreshold, _set_changeThreshold, doc="todo")

    def _get_HillCoeff(self):
        return self._HillCoeff
    def _set_HillCoeff(self, HillCoeff):
        if isinstance(HillCoeff, (int, long, float)):
            self._HillCoeff = HillCoeff
        else:
            raise TypeError("HillCoeff argument must be a number")
    HillCoeff = property(_get_HillCoeff, _set_HillCoeff, doc="todo")

    def normalise(self, **kargs):
        """Performs the normalisation using the :attr:`mode` attribute"""
        if self.verbose:
            print("normalise using the mode '%s'" % self.mode)

        if self.mode == "time":
            res = self.time_normalisation(**kargs)
        elif self.mode == "control":
            self.control_normalisation(**kargs)
        else:
            raise NotImplementedError()
        return res 

    def time_normalisation(self):
        raise NotImplementedError

    def control_normalisation(self):
        raise NotImplementedError



class NormaliseMIDAS(NormaliseMIDASBase):
    r"""Class dedicated to the normalisation of MIDAS data

    Before normalisation, the measurements that are out of the dynamic 
    range [:attr:`detection`; :attr:`saturation`] are tagged to be ignored.

    The fold change matrix is computed with a choice of algorithm. The following is
    the mode="time" case (see :meth:`normalise`):

    .. math:: 

        \hat{x} = \frac{\left\lvert X(t) - X(t_0) \right\lvert }{ X(t_0)}

    Then, a penalty coefficient is computed as follows:

    .. math:: P(t) = \frac{X(t)}{ EC_{50}^{(noise)} + X(t)}


    and the a new matrix is computed using a Hill transformation:

    .. math::

       H(t) = \frac{X^{k_H}}{ {EC_{50}^{(data)}}^{k_H} + X^{k_H} }

    rescale negative values. 

    For each specy over all experiment and time, if a negative value is found and then the column is rescaled as follows:

    .. math:: X(t) = P(t) H(t)

    .. math:: X_{s}(t) = \frac{X_{s}(t) - m_s }{M_s - m_s}

    where m_s and M_s are the minimum and maximum value over time and 
    experiment for the given specy :math:`s`.
    

    


    """
    def __init__(self, data, mode="time", verbose=True, saturation=np.inf, 
                 detection=0., EC50noise=0., EC50data=0.5, HillCoeff=2.,
                changeThreshold=0., rescale_negative=True):

        super(NormaliseMIDAS, self).__init__(mode=mode, verbose=verbose,
                saturation=saturation, detection=detection, EC50noise=EC50noise,
                EC50data=EC50data, HillCoeff=HillCoeff,
                changeThreshold=changeThreshold)
        """.. rubric:: constructor

        :param data: the MIDAS data. Could be a filename, an instance of MIDASReader 
            or an instance of CNOGraph.
        :param mode: either "time" or "ctrl". :math:`X(t)` is a matrix with experiments as 
            rows and species as columns. If mode is "time", the relative change is X(t) - X(t=t0).
            In other word, each measurement is compared to the exact same condition at time 0.
            If mode is "ctrl", the relative change is computed relative to the
            control at the same time, which is case without stimuli, but with the same
            inhibitors. 
        :param float saturation: 
        :param float detection:
        :param float EC50noise:
        :param float EC50data:
        :param float HillCoeff:
        :param float changeThres:
        :param bool rescale_negative: 
        :param verbose: print informative messages
        

    
        """
        print("Deprecated and not maintained. Please use the XMIDAS version")
        if isinstance(data, str):
            self.midas = MIDASReader(data)
        elif isinstance(data, MIDASReader):
            self.midas = data # a reference ?
        elif isinstance(data, CNOGraph):
            self.midas = data.copy()
        else:
            raise TypeError("data must be either a filename or an instance of MIDASReader or CNOGraph")

        self.data = np.array(self.midas.cnolist.valueSignals)

        # read-only attributes
        self.rescale_negative = rescale_negative


    def dynamicRange(self):
        """Returns a mask to ignore values out of the dynamic range

        This function masks values out of the dynamic range defined by the :attr:`detection`
        and :attr:`saturation`.

	    :return: a numpy mask on the data matrix
        """
        # create a mask for the data dynamic range
        if self.verbose:
            N = len(self.data[self.data>self.saturation])
            if N>0:
                print("found %s values above saturation (%s). " % (N, self.saturation))

        # deal with saturation threshold
        data = np.where(self.data > self.saturation, np.inf, self.data)

        # here below, self.data must not be used
        if self.verbose:
            N = len(data[data<self.detection])
            if N>0:
                print("found %s values below detection (%s). " % (N, self.detection))
        # deal with detection threshold
        data = np.where(data < self.detection, np.inf, data) 
        
        if self.verbose:
            N = np.sum(np.isnan(data))
            if N>0:
                print("found %s NAN values. " % (N))

        # set NA to infinite
        data[np.isnan(data)] = np.inf
        
        return np.isfinite(data)

    def _get_masked_dynamic_range(self):
        y = np.ma.masked_where(self.dynamicRange()==False, self.data)
        return y
    
    def _get_masked_pos(self):
        return np.ma.masked_inside((self.data-self.data[0,:,:]), self.changeThreshold, np.inf)

    def _get_masked_neg(self):
        return np.ma.masked_inside((self.data-self.data[0,:,:]), -np.inf, -self.changeThreshold)

    def _get_masked_ignore(self):
        return np.ma.masked_inside((self.data-self.data[0,:,:]), -self.changeThreshold, self.changeThreshold)

    def timeNormalisation(self):
        return self.time_normalisation()

    def time_normalisation(self):
        print("WARNING:: use time_normalisation")
        print("""WARNING:: XMIDAS instead of MIDASREader. Maybe buggy and is
        deprecated. See MIDASReader doc for more deails.""")


        """Performs the normalisation over time. See the class docstring for details."""        
        # create a mask with values within the 
        y = self._get_masked_dynamic_range()
        
        # todo: right now changeThr is absolute like in CellNOptR, but it would be better
        # to implement changeThreshold in a relative manner.
        # we could also uise the langmuir function like in the paper Saez MSB 2009
        
        #1. Compute the max across all measurements for each signal, excluding 
        # the values out of the dynamic range
        signalMax = np.max(y, axis=0)
        # for debugging
        self._signalMax = signalMax 

        foldChange = abs(y-y[0,:,:])/y[0,:,:]
        # for debugging
        self._foldChange = foldChange

        # 2. get the saturation penalty using EC50noise 
        # compute the penalty for being noisy, which is calculated for each
        # measurement as the measurement divided by the max measurement across all
        # conditions and time for that particular signal (excluding values out of the
        # dynamic range).
        data = y/signalMax

        satPenalty = data / (self.EC50noise + data)
        # for debugging
        self._satPenalty = satPenalty
    
        # Now I make the data go through the Hill function
        HillData = foldChange**self.HillCoeff/((self.EC50data**self.HillCoeff)+(foldChange**self.HillCoeff))
        # for debugging
        self._HillData = HillData

        # multiply HillData and SatPenalty, matrix by matrix and element by element.
        NormData = HillData * satPenalty

        # use masked_dynamic_range to set to NAN values out of dynamic range
        NormData[y.mask] = np.nan

        # multiply negative values by -1
        #NormData[self._get_masked_pos().mask] *= -1
        NormData[self._get_masked_neg().mask] *= -1 

        # set non significant values to zero
        NormData[self._get_masked_ignore().mask] = 0
        
        # rescale negative values
        if self.rescale_negative:
            # search for min and max over each colum ignoring time=t0
            m = np.nanmin(NormData, axis=0).data[0]
            M = np.nanmax(NormData, axis=0).data[0]
            # loop over species
            for i, x in enumerate(m):
                if m[i] <0 and m[i]!=M[i]:
                    NormData[:,:,i] = (NormData[:,:,i] - m[i] ) / (M[i] - m[i])

        normdata = NormData.data
        
        # finally set to zero values that are not significant.
        return normdata


class XMIDASNormalise(NormaliseMIDASBase):
    """This is a version of normalisation.


    Note that it is 100 times slower than the version that uses numpy. However,
    it uses the XMIDAS datafrme as input and would be more convenient. Faster
    version could be implemented by providing a dataframe to numpy array.


    :param float EC50noise: EC50noise no effect if set to 0 (defaults to 0)
    :param floatEC50Data: parameter for the scaling of the data between 0 and 1, 
        default=0.5
    :param float HillCoef: Hill coefficient for the scaling of the data, default to 2
    :param EC50Noise: parameter for the computation of a penalty for data 
        comparatively smaller than other time points or conditions. No effect 
        if set to zero (default).
    :param float detection: minimum detection level of the instrument, 
        -everything smaller will be treated as noise (NA), default to 0
    :param float saturation: saturation level of the instrument, everything 
        over this will be treated as NA, default to Inf.
    :param float changeThrehold: threshold for relative change considered 
        significant, default to 0


    Once parameters are provided, you can still change them since there are
    all attributes. Thex next step is to normalise the data. 
    
    this can be done using one of :
        
        * :meth:`time_normalisation`
        * :meth:`control_normalisation`


    """
    def __init__(self, data, mode="time", verbose=True, saturation=np.inf, 
                 detection=0., EC50noise=0., EC50data=0.5, HillCoeff=2.,
                changeThreshold=0.):

        super(XMIDASNormalise, self).__init__(mode=mode, verbose=verbose,
                saturation=saturation, detection=detection, EC50noise=EC50noise,
                EC50data=EC50data, HillCoeff=HillCoeff,
                changeThreshold=changeThreshold)

        # is the data a filename ?
        if isinstance(data, str):
            data = midas.XMIDAS(data)
        elif isinstance(data, midas.XMIDAS):
            pass
        else:
            raise TypeError("Input must be a filename string or a XMIDAS instance")
            
        # FIXME: do we need a copy or just a reference could be enough ?
        self.df = data.df.copy()
        self.cellLine = data.cellLine
        self._df_ref = data # do not touch df_reference
        #self.rescale_negative = rescale_negative

        self._level_exp_name = "experiment"

    def _get_masked_neg(self):
        # note the - sign before changeThreshold
        return self.df.groupby(level=[self._level_exp_name]).apply(lambda x: x-x.ix[0]) <= -self.changeThreshold

    def _get_masked_pos(self):
        return self.df.groupby(level=[self._level_exp_name]).apply(
                lambda x: x-x.ix[0]) >= self.changeThreshold

    def _get_masked_ignore(self):
        cond1 = self.df.groupby(level=[self._level_exp_name]).apply(
                lambda x: x-x.ix[0]) >= -self.changeThreshold
        cond2 = self.df.groupby(level=[self._level_exp_name]).apply(
                lambda x: x-x.ix[0]) <= self.changeThreshold
        return cond1 & cond2

    def time_normalisation(self):
        r"""Class dedicated to the normalisation of MIDAS data


        

        Before normalisation, the measurements that are out of the dynamic 
        range [:attr:`detection`; :attr:`saturation`] are tagged to be ignored.

        The fold change matrix is computed as follows:

        .. math:: 

            F(t) = \frac{\left\lvert X(t) - X(t_0) \right\lvert }{ X(t_0)}

        Then, a penalty coefficient is computed as follows:

        .. math:: P(t) = \frac{\hat{X}(t)}{ EC_{50, noise} + \hat{X}(t)}

        where :math:`\hat{X} = X/X(t)_{max}`. A new matrix is computed using a Hill transformation:

        .. math::

           H(t) = \frac{F(t)^{k_H}}{ EC_{50, data}^{k_H} + F(t)^{k_H} }

        The data is first rescaled to take into account the noise and data:

        .. math:: X_s(t) = P(t) H(t)

        Negative values are multiplied by -1 and values that are
        non-significant are set to zero. 
                
        Finally, rescale for min and max over each colum ignoring time t0 if and only if
        rescale_scaling is On.

        .. math:: X_{s}(t) = \frac{X_s(t) - m_s }{M_s - m_s}

        where :math:`m_s` and :math:`M_s` are the minimum and maximum value over time and 
        experiment for the given specy :math:`s`.
    
    
        .. note:: this normalisation works by computing a fold change relative
            to the same condition at time 0. If the value at time zero equals zero,
            , then the fold change calculation will fails. Note, however, that in
            X(t=0)=0 is not expected in many common biochemical techniques)
        
        """
        # we will exclude the values out of the dynamic range
        y = self.df.mask((self.df>self.saturation)|(self.df<self.detection))
        
        #1. Compute the max across all measurements for each signal, 
        # will be used later on for the saturation
        signalMax = y.groupby(level=self._level_exp_name).max()

        # fold Change according to time zero
        # group by experiments to apply on each matrix the function
        # F(t) = abs(X(t)-X_{t=0})/X_{0}
        foldChange = y.groupby(level=[self._level_exp_name]).apply(
                lambda x: abs((x-x.ix[0]))/x.ix[0])

        # for debugging
        self._y = y
        self._signalMax = signalMax 
        self._foldChange = foldChange

        # 2. Get the saturation penalty using EC50noise 
        # compute the penalty for being noisy, which is calculated for each
        # measurement as the measurement divided by the max measurement across all
        # conditions and time for that particular signal (excluding values out of the
        # dynamic range). This is P(t)
        data = y.divide(signalMax, level=self._level_exp_name)
        satPenalty = data / (self.EC50noise + data)
        # for debugging
        self._satPenalty = satPenalty
    
        # 3. Now we transform the data through a Hill function
        HillData = foldChange**self.HillCoeff/ \
            ((self.EC50data**self.HillCoeff)+(foldChange**self.HillCoeff))
            
        # for debugging
        self._HillData = HillData

        # multiply HillData and SatPenalty, matrix by matrix and element by element.
        NormData = HillData * satPenalty

        # use masked_dynamic_range to set to NAN values out of dynamic range
        # already done with the use of dataframe
        # NormData[y.mask] = np.nan

        # multiply negative values by -1  ?? why that this is from the original
        # paper/CellNOptR
        NormData[self._get_masked_neg()] *= -1

        # set non significant values to zero
        NormData[self._get_masked_ignore()] = 0

        # rescale negative values
        
        # search for min and max over each colum ignoring time=t0
        m = NormData.groupby(level=self._level_exp_name).min()
        M = NormData.groupby(level=self._level_exp_name).max()

        # if minimum  is negative and minimum != maximum 
       
        # FIXME: check this code. 
        cond = (m < 0) & (m!=M)
        m[cond==False] = 0
        M[cond==False] = 1
        NormData = NormData.sub(m, level=self._level_exp_name)
        NormData = NormData.divide(M-m, level=self._level_exp_name)

        return NormData
        
        
    def get_experiments_with_same_control(self):

        controls = self.get_control_name()
        mapping = {}
        for control in controls:
            mapping[control] = []
        for exp in self._df_ref.experiments.index:
            control = self._get_control(exp)
            if control != exp:
                mapping[control].append(exp)
        return mapping
        
    def get_control_name(self):
        """Return experiment name that are control (i.e., stimuli are off)"""
        name = self._df_ref.experiments[self._df_ref.stimuli.sum(axis=1)==0].index        
        return name
        
        
    def _get_control(self, experiment_name):
        inhibitors = self._df_ref.inhibitors.ix[experiment_name]
        # here is a sub selction where experiment matches the experiment_name
        mask = (self._df_ref.inhibitors == inhibitors).all(axis=1)
        # indices contains all experiment that have the same inhibitors
        indices = self._df_ref.inhibitors[mask].index
                
        # now from those experiment, which one is the control (i.e., all stimuli are off)
        stimuli = self._df_ref.stimuli.ix[indices]
        mask = stimuli.sum(axis=1)==0
        control = stimuli[mask].index
        
        # TODO assert control is unique
        assert len(control) == 1
        return control[0]
        
        
    def control_normalisation(self):
        """

        In the control normalisation, the relative change is computed 
        relative to the control experiment at the same time. The control  
        being the experiment where all stimuli are zero but inhibitors 
        re identical 
        
        .. todo:: check that a data set has these experiments.
        
        
        .. note:: the time zero case is a special case. Indeed, even
            if provided, control is ignored. The t0 data is set to zero 
            everywhere since only two measurements were made: with and
            without inhibitor(s) and these measurements have been 
            copied across corresponding position; we assume that the 
            inhibitors are already present at time 0 when we 
            add the stimuli to find the right row to normalise.
    
            
        .. note:: for now, the control is chosen as the experiment where
            all stimuli are zero.
            
            
            changeTHresholdcan be a scalar or a time series (pandas) or a list 
        
        """
        """control = self.get_control_name()
        # we will exclude the values out of the dynamic range
        y = self.df.mask((self.df>self.saturation)|(self.df<self.detection))
        
        #1. Compute the max across all measurements for each signal, 
        # will be used later on for the saturation
        signalMax = y.groupby(level=self._level_exp_name).max()

        # fold Change according to time zero
        # group by experiments to apply on each matrix the function
        # F(t) = abs(X(t)-X_{t=0})/X_{0}
        foldChange = y.groupby(level=[self._level_exp_name]).apply(
                lambda x: abs((x-x.ix[0]))/x.ix[0])
        
        #y.ix['undefined'].ix['experiment_0'] = 0
        
        # FIXME is that correct ??? need a complicated example
        ctrl = y.ix[self.cellLine].ix[control]
        norm = abs(y.sub(ctrl, level="time"))
        foldChange = norm.divide(y.ix[self.cellLine].ix[control], level='time')
    
        # for debugging
        # signalMax should be on experiment_1 only not all of them.
        self._signalMax = signalMax.ix[control]
        self._foldChange = foldChange
        """
        
        # we will exclude the values out of the dynamic range
        y = self.df.mask((self.df>self.saturation)|(self.df<self.detection))
        
        # Note the double max to max over signals and time
        signalMax = y.groupby(level=['cellLine', 'experiment']).max().max()
        self._signalMax = signalMax
        #experiment = list(set(y.reset_index()['experiment']))
        
        foldChange = y.copy()
        diff = y.copy()
        # FIXME there is probably a nice way to handle the following without for loop but 
        # this is quite tricky and did not manage so for now, let us use for loops.
        # besides, this way looks easier for debugging purposes.
        for exp in self._df_ref.experiments.index:
            control = self._get_control(exp)
            #if control == exp:
            if 0==1:
                # this is a control, let us skip it for now
                continue
            else:
                # according to       http://stackoverflow.com/questions/17552997/how-to-update-a-subset-of-a-multiindexed-pandas-dataframe?rq=1
                # get_level_values is the fastest way 
                df1 = y[y.index.get_level_values('experiment') == control]
                df2 = y[y.index.get_level_values('experiment') == exp]
                # !!! here, we use df2-df1.values not the inverse in order to 
                # maje sure that the update is made on the experiment of the data
                #, not the control. The inverse would be buggy. 
                foldChange.update( abs(df2 -df1.values)/df1.values )
                diff.update(df2 -df1.values)
        self._foldChange = foldChange 
        self._diff = diff
              
        # 2. Get the saturation penalty using EC50noise 
        # compute the penalty for being noisy, which is calculated for each
        # measurement as the measurement divided by the max measurement across all
        # conditions and time for that particular signal (excluding values out of the
        # dynamic range). This is P(t)
        self._y = y.copy()
        data = y.divide(signalMax, level=self._level_exp_name)
        satPenalty = data / (self.EC50noise + data)
        # for debugging
        self._satPenalty = satPenalty
    
        # 3. Now we transform the data through a Hill function
        HillData = foldChange**self.HillCoeff/((self.EC50data**self.HillCoeff)+(foldChange**self.HillCoeff))
        # for debugging
        self._HillData = HillData
        
        # multiply HillData and SatPenalty, matrix by matrix and element by element.
        NormData = HillData * satPenalty
        self._NormData = NormData.copy()

        # use masked_dynamic_range to set to NAN values out of dynamic range
        # already done with the use of dataframe
        # NormData[y.mask] = np.nan

        # multiply negative values by -1  ?? why that this is from the original
        # paper/CellNOptR
        masked_neg = diff < self.changeThreshold
        NormData[masked_neg] *= -1
        self._NormData = NormData.copy()

        # set non significant values to zero FIXME to be checked
        cond1 = diff >= -self.changeThreshold
        cond2 = diff <= self.changeThreshold
        masked_ignore = cond1 & cond2
        
        NormData[masked_ignore] = 0

        # search for min and max over each colum ignoring time=t0
        m = NormData.min(level="experiment")
        M = NormData.max(level="experiment")

        # if minimum  is negative and minimum != maximum 
       
        # FIXME: check this code. 
        cond = (m < 0) & (m!=M)
        m[cond==False] = 0
        M[cond==False] = 1
        NormData = NormData.sub(m, level="experiment")
        NormData = NormData.divide(M-m, level="experiment")

        return NormData
