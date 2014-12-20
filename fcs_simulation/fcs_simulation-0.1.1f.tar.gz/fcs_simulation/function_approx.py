#! /usr/bin/python

import numpy as np

class LookupTable(object):
    def __init__(self, e_i_specs, initial_value=None):
        ## *e_i_specs : [(e_i min, e_i max, delta e_i)]
        self.e_i_specs = e_i_specs
        print e_i_specs
        e_i_lengths = [extents[1]-extents[0] for extents in e_i_specs]
        e_i_counts = [int(e_i_length/extents[2]) for e_i_length, extents in zip(e_i_lengths, e_i_specs)]
        if initial_value == None:
            self.table = np.random.rand(*tuple(e_i_counts))
        else:
            self.table = np.ones(e_i_counts)*initial_value
        
    def getIndex(self, position):
        return tuple([(e_i - e_i_min)/e_i_delta for (e_i, (e_i_min, e_i_max, e_i_delta)) in zip(position, self.e_i_specs)])
    def getPosition(self, multi_index):
        pass
    def __getitem__(self, position):
        return self.table[self.getIndex(position)]
    def __setitem__(self, position, value):
        self.table[self.getIndex(position)] = value
    def iterate(self):
        return LookupTableIterator(table)

class ArrayLookupTable(LookupTable):
    def __init__(self, e_i_specs, k):
        e_i_specs.append((0, k, 1))
        LookupTable.__init__(self, e_i_specs)
        
# class LookupTableIterator(object):
#     def __init__(self, table):

#         self.index
#     def __iter__(self):
#         return self
#     def next(
