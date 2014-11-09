# -*- coding: utf-8 -*-


__author__ = "Johannes Köster"
__license__ = "MIT"


import os
import logging
from collections import namedtuple

import numpy as np
import h5py


from peanut.bitencoding import preprocess_bases, preprocess_length, get_not_n_pos
from peanut.bitencoding import bitencode, bitencode_comp
from peanut.bitencoding import pack_sequence
import peanut.input
from peanut.stats import stats
from peanut.utils import is_higher_version, PeanutError


__version__ = "0.3"


H5PY_STR_DTYPE = h5py.special_dtype(vlen=bytes)


References = namedtuple("References", "names sizes encoded strand_sizes offsets positions global_size count")


def read_references(hdf5file):
    """Read references from index.

    Args:
        hdf5file (h5py.File): an HDF5 file object

    Returns:
        References: The references.
    """
    if not "peanut_index" in hdf5file:
        raise PeanutError("This HDF5 file does not contain a valid peanut index.")
    index = hdf5file["peanut_index"]
    version = index.attrs["version"]
    if is_higher_version(__version__, version):
        raise PeanutError(
            "The peanut index is outdated (version {}, need {}). "
            "Please create a new one for this version of peanut.".format(
            version, __version__))
    elif is_higher_version(version, __version__):
        raise PeanutError(
            "The peanut index is too new (version {}, need {}). "
            "Please create a new one for this version of peanut.".format(
            version, __version__))

    names = index["sqnames"].value
    sq = index["sq"]

    refs = [sq[ref] for ref in names]
    strands = [(ref, strand) for ref in refs for strand in ref]

    return References(
        names=names,
        sizes=[ref.attrs["size"] for ref in refs],
        encoded=[ref[strand]["encoded"].value for ref, strand in strands],
        strand_sizes=np.array([ref.attrs["size"] for ref, strand in strands], dtype=np.int32),
        offsets=np.array([ref[strand].attrs["offset"] for ref, strand in strands], dtype=np.int32),
        positions=[ref[strand]["pos"].value for ref, strand in strands],
        global_size=sum(ref.attrs["size"] for ref in refs) * 2,
        count=sum(1 for ref in refs) * 2)


def write_references(hdf5file, fastapath, filtration, min_repeat_count=1000):
    """Write references to HDF5.

    Args:
        hdf5file (h5py.File):   an HDF5 file object
        fastapath (generator):  an opened fasta file
        filtration (peanut.filtration.Filtration): a filtration object
        min_repeat_count (int): minimum count for a q-gram to be masked as repeat
    """
    index = hdf5file.create_group("peanut_index")
    index.attrs["version"] = __version__
    sq = index.create_group("sq")

    names = list()
    cache = list()
    for reference in peanut.input.read_fasta(fastapath):
        names.append(reference.name)

        refsize = len(reference.seq)
        # load the reverse sequence since we run myers algorithm in backward direction
        seq = preprocess_length(reference.seq[::-1])
        refpos = np.unique(get_not_n_pos(seq) // 16)

        ref = sq.create_group(reference.name)
        ref.attrs["size"] = refsize
        for plusstrand in (True, False):
            strand = ref.create_group("+" if plusstrand else "-")

            if plusstrand:
                encoded = pack_sequence(bitencode(preprocess_bases(seq)))
                offset = 0
            else:
                encoded = pack_sequence(bitencode_comp(preprocess_bases(seq))[::-1])
                refpos = np.array((len(encoded) - refpos - 1)[::-1], dtype=np.int32)  # make contiguous
                if refsize % 16:
                    # unused bases at the end of the forward strand become the offset of the reverse
                    offset = 16 - refsize % 16

            # cache the reference for repeat masking
            cache.append((strand, encoded, refpos, refsize))

            strand.create_dataset("encoded", data=encoded)
            #strand.create_dataset("pos", data=refpos)
            strand.create_dataset("sequence", data=np.fromstring(reference.seq, dtype=np.uint8))
            strand.attrs["offset"] = offset

    # store the reference names in the correct order (same as in fasta file)
    sqnames = index.create_dataset("sqnames", [len(names)], dtype=H5PY_STR_DTYPE)
    sqnames[:] = names

    logging.info("masking repeats...")
    for strand, encoded, refpos, refsize in cache:
        # create an index over the reference
        cl_reference = filtration.cl.copy(encoded)
        cl_reference_pos = filtration.cl.copy(refpos)
        filtration.reference_index(cl_reference, cl_reference_pos, refsize)
        cl_reference_pos_repeats = filtration.cl.zeros_like(cl_reference_pos)
        del cl_reference

        # iterate over all other references and count repeats
        for _, other_encoded, other_refpos, other_refsize in cache:
            filtration.cl.pool.free_held()
            cl_other_reference = filtration.cl.copy(other_encoded)
            cl_other_reference_pos = filtration.cl.copy(other_refpos)
            filtration.count_repeats(cl_reference_pos_repeats, cl_other_reference, cl_other_reference_pos, other_refsize)
            del cl_other_reference
            del cl_other_reference_pos

        # mask repeats
        notrepeat = cl_reference_pos_repeats.get() < min_repeat_count
        del cl_reference_pos_repeats

        refpos = cl_reference_pos.get()[notrepeat]
        del cl_reference_pos

        # sort refpos by encoded q-grams to improve coalescense when q-group index is queried
        refpos = refpos[np.argsort(encoded[refpos])]

        strand.create_dataset("pos", data=refpos)
