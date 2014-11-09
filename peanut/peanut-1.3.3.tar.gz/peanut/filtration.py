# -*- coding: utf-8 -*-


__author__ = "Johannes Köster"
__license__ = "MIT"


import logging
from collections import Counter

import numpy as np
import pyopencl as cl
import pyopencl.array as clarray
import pyopencl.algorithm as clalg
from pyopencl.elementwise import ElementwiseKernel

from peanut.utils import to_multiple, MAXUINT
import sys


INDEX_SIZE = MAXUINT // 32 + 1
OUTER_POS_SIZE = INDEX_SIZE // 2 + 1


class Filtration:
    def __init__(
            self,
            blocksize=512,
            cldevice=None):

        self.blocksize = blocksize
        self.cl = cldevice
        self.cl_queries = None
        self.cl_index = None
        self.cl_occ_outer_pos = None
        self.cl_occ_pos = None
        self.cl_occ = None
        self.queries_width = None

        self.cl.compile(
            "filtration",
            options="",  #"-cl-nv-verbose" if not cldevice.cpu else "-g -cl-opt-disable",
            index_size=INDEX_SIZE,
            outer_pos_size=OUTER_POS_SIZE)

    def cleanup(self):
        if self.cl_queries is not None:
            del self.cl_queries
            self.cl_queries = None
        if self.cl_index is not None:
            del self.cl_index
            del self.cl_occ_outer_pos
            del self.cl_occ_pos
            del self.cl_occ
            self.cl_index = None
            self.cl_occ_outer_pos = None
            self.cl_occ_pos = None
            self.cl_occ = None

    def index(self, cl_queries, cl_queries_sizes):
        """Create a q-group index of the given queries."""
        self.cleanup()
        self.cl_queries = cl_queries
        queries_size, self.queries_width = cl_queries.shape

        self.cl_index = self.cl.zeros(
            INDEX_SIZE, np.uint32)

        dim0 = self.blocksize // (self.queries_width * 16)
        if not dim0:
            dim0 = 1
        elif dim0 % 2:
            dim0 += 1
        work_items = (to_multiple(queries_size, dim0), self.queries_width, 16)
        work_groups = dim0, self.queries_width, 16
        logging.debug("Kernel config of q-group index building: {}; {}".format(work_items, work_groups))
        self.cl.filtration.create_queries_index(
            self.cl.queue,
            work_items,
            work_groups,
            np.int32(queries_size),
            cl_queries.data,
            cl_queries_sizes.data,
            self.cl_index.data)

        work_items = (to_multiple(OUTER_POS_SIZE, self.blocksize),)
        work_groups = (self.blocksize,)
        # do not fill the first element of popcount for proper cumsum, hence one element more
        cl_popcount = self.cl.zeros(OUTER_POS_SIZE, np.int32)
        self.cl.filtration.popcount_index(
            self.cl.queue,
            work_items,
            work_groups,
            self.cl_index.data,
            cl_popcount.data
        )

        self.cl_occ_outer_pos = clarray.cumsum(cl_popcount)

        del cl_popcount

        # one element more since we leave the first element empty for cumsumming
        occ_count_size = self.cl_occ_outer_pos[-1].get().item() + 1
        cl_occ_count = self.cl.zeros(occ_count_size, np.int32)

        work_items = (to_multiple(queries_size, self.blocksize),)
        work_groups = (self.blocksize,)
        self.cl.filtration.create_queries_occ_count(
            self.cl.queue,
            work_items,
            work_groups,
            np.int32(queries_size),
            np.int32(self.queries_width),
            cl_queries.data,
            cl_queries_sizes.data,
            self.cl_index.data,
            self.cl_occ_outer_pos.data,
            cl_occ_count.data
        )
        self.cl_occ_pos = clarray.cumsum(cl_occ_count)

        occ_size = self.cl_occ_pos[-1].get().item()
        assert occ_size <= queries_size * self.queries_width * 16

        self.cl_occ = self.cl.empty(occ_size, np.int32)
        cl_occ_count.fill(np.int32(0))
        self.cl_occ.fill(np.int32(-1))

        work_items = (to_multiple(queries_size, self.blocksize),)
        work_groups = (self.blocksize,)
        self.cl.filtration.create_queries_occ(
                self.cl.queue,
                work_items,
                work_groups,
                np.int32(queries_size),
                np.int32(self.queries_width),
                cl_queries.data,
                cl_queries_sizes.data,
                self.cl_index.data,
                self.cl_occ_outer_pos.data,
                self.cl_occ_pos.data,
                cl_occ_count.data,
                self.cl_occ.data
            )

        del cl_occ_count

    def filter(self, cl_reference, cl_reference_pos):
        """Filter hits given the reference."""
        n = len(cl_reference_pos)

        hits_count = 0
        if n:
            work_items = to_multiple(n, self.blocksize),
            work_groups = self.blocksize,

            cl_hits = self.cl.zeros(n + 1, np.int32)
            self.cl.filtration.filter_reference(
                self.cl.queue,
                work_items,
                work_groups,
                np.int32(n),
                cl_reference.data,
                cl_reference_pos.data,
                self.cl_index.data,
                self.cl_occ_outer_pos.data,
                self.cl_occ_pos.data,
                cl_hits.data
            )

            cl_reference_hits_pos = self.cl.copy_if_ext(cl_reference_pos, cl_hits, predicate="cond[i+1] > 0")
            del cl_reference_pos

            old_n, n = n, len(cl_reference_hits_pos)

            cl_hits = self.cl.copy_if(cl_hits, "i == 0 || ary[i] > 0")
            cl_hits_start = clarray.cumsum(cl_hits)
            del cl_hits

            hits_count = cl_hits_start[-1].get().item()

        cl_hit_positions = self.cl.empty(hits_count, np.int32)
        cl_hit_queries = self.cl.empty(hits_count, np.int32)

        if hits_count:
            queries_width_bases = self.queries_width * 16
            work_items = to_multiple(n, self.blocksize),
            work_groups = self.blocksize,
            self.cl.filtration.create_candidates(
                self.cl.queue,
                work_items,
                work_groups,
                np.int32(n),
                np.int32(queries_width_bases),
                cl_reference.data,
                cl_reference_hits_pos.data,
                self.cl_index.data,
                self.cl_occ_outer_pos.data,
                self.cl_occ_pos.data,
                self.cl_occ.data,
                cl_hits_start.data,
                cl_hit_positions.data,
                cl_hit_queries.data
            ).wait()

            del cl_hits_start
            del cl_reference_hits_pos

        return cl_hit_positions, cl_hit_queries

    def reference_index(self, cl_reference, cl_reference_pos, reference_size):
        """Create a q-group index of the given reference."""
        reference_pos_size = len(cl_reference_pos)
        reference_pos_work_items = (to_multiple(reference_pos_size, self.blocksize),)
        reference_pos_work_groups = (self.blocksize,)

        self.cleanup()
        self.cl_index = self.cl.zeros(INDEX_SIZE, np.uint32)

        self.cl.filtration.create_reference_index(
            self.cl.queue,
            reference_pos_work_items,
            reference_pos_work_groups,
            np.int32(reference_size),
            np.int32(reference_pos_size),
            cl_reference.data,
            cl_reference_pos.data,
            self.cl_index.data)

        work_items = (to_multiple(OUTER_POS_SIZE, self.blocksize),)
        work_groups = (self.blocksize,)
        # do not fill the first element of popcount for proper cumsum, hence one element more
        cl_popcount = self.cl.zeros(OUTER_POS_SIZE, np.int32)
        self.cl.filtration.popcount_index(
            self.cl.queue,
            work_items,
            work_groups,
            self.cl_index.data,
            cl_popcount.data
        )

        self.cl_occ_outer_pos = clarray.cumsum(cl_popcount)
        del cl_popcount

        # one element more since we leave the first element empty for cumsumming
        occ_count_size = self.cl_occ_outer_pos[-1].get().item() + 1
        cl_occ_count = self.cl.zeros(occ_count_size, np.int32)

        self.cl.filtration.create_reference_occ_count(
            self.cl.queue,
            reference_pos_work_items,
            reference_pos_work_groups,
            np.int32(reference_size),
            np.int32(reference_pos_size),
            cl_reference.data,
            cl_reference_pos.data,
            self.cl_index.data,
            self.cl_occ_outer_pos.data,
            cl_occ_count.data
        )

        self.cl_occ_pos = clarray.cumsum(cl_occ_count)

        occ_size = self.cl_occ_pos[-1].get().item()

        self.cl_occ = self.cl.empty(occ_size, np.int32)
        cl_occ_count.fill(np.int32(0))
        self.cl_occ.fill(np.int32(-1))

        work_items = (to_multiple(reference_pos_size, self.blocksize),)
        work_groups = (self.blocksize,)
        self.cl.filtration.create_reference_occ(
                self.cl.queue,
                reference_pos_work_items,
                reference_pos_work_groups,
                np.int32(reference_size),
                np.int32(reference_pos_size),
                cl_reference.data,
                cl_reference_pos.data,
                self.cl_index.data,
                self.cl_occ_outer_pos.data,
                self.cl_occ_pos.data,
                cl_occ_count.data,
                self.cl_occ.data
            ).wait()

        #assert np.all(self.cl_occ_outer_pos.get() <= self.cl_occ_pos.shape[0])
        #assert self.cl_occ_pos.shape[0] - self.cl_occ_outer_pos[-1].get().item() < 16
        #assert np.all(self.cl_occ_pos.get() <= self.cl_occ.shape[0])
        #assert np.all(self.cl_occ_pos.get() >= 0)
        #assert np.all(self.cl_occ_outer_pos.get() >= 0)
        #assert np.all(self.cl_occ.get() < reference_pos_size) and np.all(self.cl_occ.get() >= 0)

    def count_repeats(self, cl_reference_pos_repeats, cl_reference, cl_reference_pos, reference_size):
        """Count repetetive q-grams."""
        reference_pos_size = len(cl_reference_pos)
        reference_pos_work_items = (to_multiple(reference_pos_size, self.blocksize), 16)
        reference_pos_work_groups = (self.blocksize // 16, 16)

        #assert np.all(self.cl_occ.get() >= 0)
        #assert np.all(self.cl_occ.get() < cl_reference_pos_repeats.shape[0])

        self.cl.filtration.count_reference_repeats(
            self.cl.queue,
            reference_pos_work_items,
            reference_pos_work_groups,
            np.int32(reference_size),
            np.int32(reference_pos_size),
            np.int32(self.cl_occ_pos.shape[0] - 1),
            cl_reference.data,
            cl_reference_pos.data,
            self.cl_index.data,
            self.cl_occ_outer_pos.data,
            self.cl_occ_pos.data,
            self.cl_occ.data,
            cl_reference_pos_repeats.data
        ).wait()
