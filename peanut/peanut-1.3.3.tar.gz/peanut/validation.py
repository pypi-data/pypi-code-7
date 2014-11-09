# -*- coding: utf-8 -*-


__author__ = "Johannes Köster"
__license__ = "MIT"


import logging
import pyopencl as cl
from pyopencl.elementwise import ElementwiseKernel
import pyopencl.array as clarray
import numpy as np

from peanut.utils import to_multiple


class Validation:
    def __init__(
            self,
            blocksize=512,
            min_score=40,
            cldevice=None):

        self.blocksize = blocksize
        self.cl = cldevice
        self.score_filter = "{{}}[i] >= {min_score}".format(min_score=min_score).format

        self.cl.compile(
            "validation",
            options="",  #"-cl-nv-verbose" if not cldevice.cpu else "",
            band_width=32,
            min_score=min_score,
            blocksize=blocksize)

        self.knl_count_query_hits = ElementwiseKernel(self.cl.ctx,
            "__global const int* hit_queries, "
            "__global const int* hit_scores, "
            "__global int* query_hits_count ",
            """
            if(hit_scores[i] < {min_score})
                PYOPENCL_ELWISE_CONTINUE;

            const int query = hit_queries[i];
            atomic_inc(&query_hits_count[query + 1]);

            """.format(min_score=min_score),
            "count_query_hits")

        self.knl_fill_query_hits = ElementwiseKernel(self.cl.ctx,
            "__global const int* hit_queries, "
            "__global const int* hit_scores, "
            "__global const int* hit_positions, "
            "__global int* query_hits_pos, "
            "__global int* query_hit_scores, "
            "__global int* query_hit_positions ",
            """
            const int hit_score = hit_scores[i];
            if(hit_score < {min_score})
                PYOPENCL_ELWISE_CONTINUE;

            const int k = atomic_inc(&query_hits_pos[hit_queries[i]]);
            query_hit_scores[k] = hit_score;
            query_hit_positions[k] = hit_positions[i];

            """.format(min_score=min_score),
            "fill_query_hits")


    def validate(self, cl_reference, reference_size, reference_offset, cl_queries, cl_queries_sizes, cl_hit_positions, cl_hit_queries):
        """Validate hits."""
        queries_width = cl_queries.shape[1]
        hits_size = len(cl_hit_positions)
        cl_hit_scores = self.cl.empty_like(cl_hit_queries)
        logging.debug("validating {} hits".format(hits_size))

        chunk = 1000000
        for offset in range(0, hits_size, chunk):
            work_items = (to_multiple(min(chunk, hits_size - offset), self.blocksize),)
            work_groups = (self.blocksize,)
            self.cl.validation.validate_hits(
                self.cl.queue,
                work_items,
                work_groups,
                np.int32(hits_size),
                np.int32(reference_size),
                np.int32(reference_offset),
                np.int32(queries_width),
                np.int32(offset),
                cl_reference.data,
                cl_queries.data,
                cl_queries_sizes.data,
                cl_hit_positions.data,
                cl_hit_queries.data,
                cl_hit_scores.data
            )

        cl_query_hits_count = self.cl.zeros(len(cl_queries) + 1, dtype=np.int32)
        self.knl_count_query_hits(cl_hit_queries, cl_hit_scores, cl_query_hits_count)
        cl_query_hits_pos = clarray.cumsum(cl_query_hits_count)
        del cl_query_hits_count
        hits_count = cl_query_hits_pos[-1].get().item()

        cl_query_hit_positions = self.cl.empty(hits_count, np.int32)
        cl_query_hit_scores = self.cl.empty(hits_count, np.int32)
        _cl_query_hits_pos = cl_query_hits_pos.copy()
        self.knl_fill_query_hits(cl_hit_queries, cl_hit_scores, cl_hit_positions, _cl_query_hits_pos, cl_query_hit_scores, cl_query_hit_positions)

        del cl_hit_positions
        del cl_hit_scores
        del _cl_query_hits_pos

        return cl_query_hit_positions, cl_query_hit_scores, cl_query_hits_pos
