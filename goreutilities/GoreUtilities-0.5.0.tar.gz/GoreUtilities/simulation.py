#!/usr/bin/env python
"""
Provides a simulator class that:
* Allows the user to easily iterate over different simulation parameters
* Allows saving/loading results into files

TODO/THOUGHTS:
    - Implement a filter method that will return
    simulations results that pass a certain criteria
    - Add grid_plot method
    - BaseSimulatior.pars[slice] -> To return parameters
    - BaseSimulatior.results[slice] -> To return result?
    - BaseSimulatior[slice] -> To return result? or par, result tuple?
    - Rewrite this to using pandas containers? (Of course, one issue would be ndpanels!)
        - That is definitely very convenient for using apply/filter methods etc.
"""
from util import get_files, save, load, to_list
from GoreUtilities import create_grid_layout, graph
import itertools
import time
import numpy
import types
import pylab as pl
import pandas
import copy
import warnings

class Indexer(object):
    def __init__(self, parent, method_name):
        self.parent = parent
        self.method_name = method_name
    def __getitem__(self, key):
        return getattr(self.parent, self.method_name)(key)

class LoadableObject(object):
    """
    Object provides interface
    for loading / saving object into file
    """
    # TODO: Refactor to use BaseObject in util. Will need to remove the __repr__

    def save(self, path):
        save(self, path)

    @classmethod
    def load(cls, path):
        return load(path)

def _test_func(**kwargs):
    print kwargs
    return kwargs

class BaseSimulator(LoadableObject):
    def __init__(self, simulation_function, loop_pars=None, **par_dict):
        """
        Parameters
        ---------------
        simulation_function : callable
            A callable that does something with the parameters that are passed to it and returns a result.

        loop_pars : 'str' | list of 'str'
            name(s) of parameters that will be looped over

        par_dict : parameters to be fed into the simulator
        """
        if loop_pars is not None:
            self.loop_pars = to_list(loop_pars)
            self.loop_par_values = [par_dict.pop(par_name) for par_name in self.loop_pars]

            f = lambda x : [x] if isinstance(x, (int, float, types.FunctionType)) else to_list(x) # TODO: Need to fix to_list function to work with integers / floats

            self.loop_par_values = map(f, self.loop_par_values)
        else:
            self.loop_pars = None
            self.loop_par_values = None

        self.func = simulation_function
        self.pars = Indexer(self, 'get_pars')

        # Important keep this last
        self.par_dict = par_dict

    def __call__(self, **kwargs):
        """ A short hand to run the simulation. Returns a reference to self. """
        self.run(**kwargs)
        return self

    def _get_iterator(self):
        return itertools.product(*self.loop_par_values)

    def run(self, verbose=False):
        """
        Runs the simulation.

        If loop_pars have been defined, then iterates over the values
        of the loop parameters feeding each value into the simulator function.
        """
        self.tic = time.time()

        if self.loop_pars is not None:
            shape = tuple([len(v) for v in self.loop_par_values])

            self.results = numpy.empty(shape, dtype=tuple)

            for index, par_values in enumerate(self._get_iterator()):
                par_dict = self._make_par_dict(*par_values)
                loc = numpy.unravel_index(index, shape, 'C')
                self.results[loc] = self.func(**par_dict)
        else:
            par_dict = self._make_par_dict()
            self.results = self.func(**par_dict)

        self.toc = time.time()

    def _make_par_dict(self, *par_values):
        par_dict = copy.deepcopy(self.par_dict)
        if self.loop_pars is not None:
            for i, l in enumerate(self.loop_pars):
                par_dict[l] = par_values[i]
        return par_dict

    def get_pars(self, loc):
        """
        Returns the parameters used for simulation at location loc

        Parameters
        -----------
        loc : location in an ndarray

        Returns
        ---------
        Simulation parameters : dictionary
        """

        if isinstance(loc, types.StringTypes):
            raise TypeError('Indexing using strings is not currently supported')
        if isinstance(loc, list):
            raise Exception('Please use tuple instead of list for loc')

        if hasattr(loc, '__iter__'): # Quick fix. This will be a bug for when strings are used for indexing.
            par_values = [v[loc[i]] for i, v in enumerate(self.loop_par_values)]
        else:
            par_values = [self.loop_par_values[0][loc]]
        return self._make_par_dict(*par_values)

    def apply(self, callable, dtype, applyto='result', output_type='pandas'):
        """
        Applies the callable function over the results returning a numpy array
        of dtype

        Parameters
        ------------

        callable : a callable
            Accepts as input a single result
            Returns some processed output
        dtype : type of output to expect from the callable
        applyto : 'result' | 'pars' | 'both'
            if 'both', function must accept results, pars
        output_type: 'pandas' | None
            if 'pandas', then the simulator will try to convert the result to a pandas data object. (only implemented for 1d and 2d)
        """
        output = numpy.empty(self.results.shape, dtype=dtype)
        for loc, result in numpy.ndenumerate(self.results):
            if applyto == 'result':
                output[loc] = callable(result)
            elif applyto == 'pars':
                output[loc] = callable(self.pars[loc])
            elif applyto == 'both':
                output[loc] = callable(result, self.pars[loc])
            else:
                raise Exception("applyto must be 'result', 'pars' or 'both'")

        if output_type == 'pandas' and self.loop_pars is not None:
            ndim = len(self.loop_pars)
            if ndim == 1:
                output = pandas.Series(data=output, index=self.loop_par_values[0])
                output.index.name = self.loop_pars[0]
            elif ndim == 2:
                output = pandas.DataFrame(data=output, index=self.loop_par_values[0], columns=self.loop_par_values[1])
                output.index.name = self.loop_pars[0]
                output.columns.name = self.loop_pars[1]
            else:
                raise Exception('Not implemented for ndim > 2')
        return output

    def plot(self, callable, **kwargs):
        """ Plots all curves on a single axes """
        for loc, result in numpy.ndenumerate(self.results):
            if isinstance(callable, str):
                getattr(result, callable)(**kwargs) # Used to access object properties
            elif hasattr(callable, '__call__'):
                callable(result, **kwargs)

    def grid_plot(self, callable, xlim='auto', ylim='auto',
                row_labels='auto', col_labels='auto',
                rlabel_format = '{}', clabel_format='{}',
                row_label_xoffset=None, col_label_yoffset=None,
                autolabel=True,
                wspace=0, hspace=0,
                xlabelpad=0.0, ylabelpad=0.0,
                **kwargs):
        """
        Plots a 2d matrix with subplots for each simulation result.
        At the moment, this only works when cycling over two parameters simulatenously.
        TODO: Fix to make it possible to do this for 1d simulations

        Parameters
        ---------------

        Callable : a callable with arguments result
        """
        # TODO: Refactor to combine with code from FlowCytometryTools
        # TODO: Fix parameter passing the way parameters are passed
        warnings.warn('Trying to deprecate this method! Please rewrite the code.')

        # Autoscaling behavior
        if xlim == 'auto' and ylim == 'auto':
            axis = 'both'
            xlim, ylim = None, None # Dirty solution
        elif xlim == 'auto':
            axis = 'x'
            xlim = None # Dirty solution
        elif ylim == 'auto':
            axis = 'y'
            ylim = None # Dirty solution
        else:
            axis = 'none'

        ndim = len(self.results.shape)

        if ndim == 1:
            row_num, col_num = self.results.shape[0], 1
            col_labels = None
            if row_labels == 'auto':
                row_labels = map(rlabel_format.format, self.loop_par_values[0])
        else: # ndim should be 2
            row_num, col_num = self.results.shape

            if col_labels == 'auto':
                col_labels = map(clabel_format.format, self.loop_par_values[1])
            if row_labels == 'auto':
                row_labels = map(rlabel_format.format, self.loop_par_values[0])

        ax_main, ax_matrix = graph.create_grid_layout(rowNum=row_num, colNum=col_num,
                    xlim=xlim, ylim=ylim,
                    row_labels=row_labels, col_labels=col_labels,
                    row_label_xoffset=row_label_xoffset, col_label_yoffset=col_label_yoffset,
                    wspace=wspace, hspace=hspace)

        for loc, ax in numpy.ndenumerate(ax_matrix):
            pl.sca(ax)

            if ndim == 1:
                loc = loc[0]

            if hasattr(callable, '__call__'):
                callable(self[loc], **kwargs)

            if xlim not in (None, 'auto'):
                pl.xlim(xlim)
            if ylim not in (None, 'auto'):
                pl.ylim(ylim)

        graph.autoscale_subplots(ax_matrix, axis)
        pl.sca(ax_main)

        if autolabel:
            if ndim == 2:
                pl.xlabel(self.loop_pars[1], size='x-large', labelpad=xlabelpad)
                pl.ylabel(self.loop_pars[0], size='x-large', labelpad=ylabelpad)
            elif ndim == 1:
                pl.ylabel(self.loop_pars[0], size='x-large', labelpad=ylabelpad)

    @property
    def shape(self):
        return self.results.shape

    def __getitem__(self, loc):
        return (self.pars[loc], self.results[loc])


if __name__ == '__main__':
    z = BaseSimulator(_test_func, ['z', 'k'], z=[1, 2, 3], k=[1, 2, 3, 4])
    #z = BaseSimulator(_test_func, p=2, loop_pars=['k'], z=[3, 10.0, 7], k=[1, 2])
    z()
    print '-'*80
    print z.apply(lambda x,y : (x, y), object, 'both')
    #print z.get_pars((2, 1))
    #print z.pars[2, 1]
    #print z.pars[0, 1]
    #print z[0, 0]
