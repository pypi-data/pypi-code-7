# -*- coding: utf-8 -*-


__author__ = "Johannes Köster"
__license__ = "MIT"


import logging
from itertools import islice, chain
from collections import namedtuple
import numpy as np

from peanut.bitencoding import bitencode, WILDCARD, pack_sequences
from peanut.bitencoding import preprocess_bases, preprocess_query_sequences
import peanut.input


Queries = namedtuple("Queries", "names encoded sizes sequences qualities count maxsize")


def read_queries(path, matespath=None, buffersize=1000000):
    """Read queries from fastq file."""
    if matespath is None:
        fq = peanut.input.open_text(path)
        all_records = peanut.input.read_fastq_buffered(fq, None, buffersize)
    else:
        assert buffersize % 2 == 0  # need to have enough buffer to keep to each query its mate
        fq1 = peanut.input.open_text(path)
        fq2 = peanut.input.open_text(matespath)
        all_records = peanut.input.read_fastq_buffered(fq1, fq2, buffersize)

    for query_names, query_sizes, query_sequences, query_qualities in all_records:

        maxquerysize = np.max(query_sizes)

        logging.debug("preprocessing queries")
        preprocessed = preprocess_query_sequences(query_sequences, maxquerysize)
        logging.debug("packing queries")
        query_encoded = pack_sequences(preprocessed)

        yield Queries(np.asarray(query_names, dtype=object), query_encoded, np.asarray(query_sizes, dtype=np.int32), np.asarray(query_sequences, dtype=object), np.asarray(query_qualities, dtype=object), len(query_names), maxquerysize)
