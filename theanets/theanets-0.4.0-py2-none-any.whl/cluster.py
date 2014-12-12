# Copyright (c) 2014 Leif Johnson <leif@leifjohnson.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''This file contains an interface for distributing network computations.'''

import climate
import collections
import itertools
import numpy as np
import numpy.random as rng
import scipy.optimize
import theano
import theano.tensor as TT
import sys

from . import dataset
from . import feedforward
from . import recurrent

logging = climate.get_logger(__name__)


class Cluster:
    '''Cluster is a thin interface for distributing computations.
    '''

    def sync(self, network):
        '''Synchronize the state of our cluster workers.

        The default implementation is a no-op.

        Parameters
        ----------
        network : theanets.Network
            A theanets Network whose state is to be synchronized across remote
            workers.
        '''
        return

    def map(self, fun, dataset):
        '''Map a function onto each element of a dataset.

        Parameters
        ----------
        fun : theano.function
            A function to call on each dataset element.
        dataset : theanets.Dataset
            A set of data to pass to the function.

        Returns
        -------
        list of ndarray :
            A list of the results from computing fun(x) on each element x in the
            given dataset.
        '''
        return [fun(*x) for x in dataset]


class IPythonCluster(Cluster):
    '''An IPython cluster can distribute computations to IPython workers.
    '''

    def __init__(self, client):
        self.client = client

    def sync(self, network):
        '''Synchronize the state of our cluster workers.
        '''
        self.client.run(network)

    def map(self, fun, dataset):
        '''
        '''
        return self.client.map(fun, dataset)
