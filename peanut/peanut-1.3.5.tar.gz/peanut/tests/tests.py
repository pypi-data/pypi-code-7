import os
import sys
import imp
import math
import pkg_resources
import numpy as np
import h5py


import peanut
from peanut import Hits
from peanut.query import read_queries, Queries
from peanut.reference import write_references, read_references, References
from peanut.filtration import Filtration
from peanut.validation import Validation
import peanut.postprocessing as postprocessing
import peanut.bitencoding as bitencoding
from peanut.utils import CLDevice, PeanutError
import peanut.input
from peanut import SCORE_MATRIX

import random
random.seed(42)


TEST_FASTA = pkg_resources.resource_filename(__name__, "test.fasta")
TEST_FASTQ = pkg_resources.resource_filename(__name__, "test.fastq")
TEST_REF_FASTA = pkg_resources.resource_filename(__name__, "reference.fasta")
TEST_REF_HDF5 = pkg_resources.resource_filename(__name__, "reference.hdf5")


try:
    cl = CLDevice(cpu=False)
except PeanutError:
    cl = CLDevice(cpu=True)


def get_file(filename):
    return pkg_resources.resource_filename(filename)


def get_filtration(blocksize=32):
    return Filtration(cldevice=cl, blocksize=blocksize)


def get_validation():
    return Validation(cldevice=cl, blocksize=32, min_score=8)


def test_read_fasta():
    names = [b"X", b"Y", b"Z"]
    sizes = [300, 7, 7]
    for exp_name, exp_size, record in zip(
        names, sizes, peanut.input.read_fasta(TEST_FASTA)):
        assert record.name == exp_name
        assert len(record.seq) == exp_size

"""
def test_read_fastq():
    names = [b"A", b"B", b"C"]
    sizes = [46, 60, 18]
    for exp_name, exp_size, record in zip(
        names, sizes, peanut.input.read_fastq(TEST_FASTQ)):
        assert record.name == exp_name
        assert len(record.seq) == exp_size
"""

def test_read_queries():
    names = [b"A", b"B", b"C", b"D"]
    sizes = [46, 60, 18, 40]
    for queries in read_queries(
        TEST_FASTQ, buffersize=5):
        assert np.all(queries.sizes == sizes)
        assert np.all(queries.names == names)


def test_bitencoding():
    sequence = b"ACTCGTAGCTCGATATAGCTAGATCGATAGCTGATATATCGCGTATCGATCGTCGATCGCT"

    preprocessed = bitencoding.preprocess_bases(sequence)

    encoded = bitencoding.pack_sequence(bitencoding.bitencode(preprocessed))
    decoded = bitencoding.bitdecode_packed(encoded)[:len(sequence)]
    assert decoded == sequence


def test_revcomp():
    sequence = b"ACTCGTAGCTCGATATAGCTAGATCGATAGCTGATATATCGCGTATCGATCGTCGATCGCT"
    comp = bitencoding.bitencode_comp(bitencoding.preprocess_bases(sequence))
    revcomp = comp[::-1]

    encoded = bitencoding.pack_sequence(revcomp)
    decoded = bitencoding.bitdecode_packed(encoded)[:len(sequence)]
    assert decoded == b"AGCGATCGACGATCGATACGCGATATATCAGCTATCGATCTAGCTATATCGAGCTACGAGT"


def test_create_reference_index():
    if os.path.exists(TEST_REF_HDF5):
        os.remove(TEST_REF_HDF5)
    with h5py.File(TEST_REF_HDF5) as hdf5file:
        write_references(hdf5file, TEST_REF_FASTA, get_filtration(), min_repeat_count=40)

    with h5py.File(TEST_REF_HDF5) as hdf5file:
        references = read_references(hdf5file)
        print(references.positions[0])
        assert set(references.positions[0]) == set([17, 13, 14, 6, 5, 7, 12, 4, 15, 16, 11, 18])


def test_pack():
    sequences = np.array(
        [list(bitencoding.bitencode(b"A" * 13 + b"GGG" + b"A" * 14 + b"GG"))],
        dtype=np.uint8)
    packed = bitencoding.pack_sequences(sequences)
    assert packed[0, 0] == int("101010" + "00" * 13, 2)
    assert packed[0, 1] == int("1010" + "00" * 14, 2)

    cl_sequences, cl_sizes = setup_queries()
    sequences = cl_sequences.get()
    assert np.all(sequences[0] == [3, 0])
    assert np.all(sequences[1] == [0, 3])
    assert np.all(sequences[2] == [int("10" * 16, 2), 0])

    del cl_sizes
    del cl_sequences


def test_index():
    cl_queries, cl_sizes = setup_queries()

    filtration = get_filtration()
    filtration.index(cl_queries, cl_sizes)

    index = filtration.cl_index.get()
    qgroup1 = 0
    qgroup2 = 89478485
    qgroup3 = 100663296
    assert index[qgroup1] == int("1001", 2)
    assert index[qgroup2] == int("1" + "0" * 10, 2)
    assert index[qgroup3] == int("1", 2)
    assert set(index.nonzero()[0]) == set((qgroup1, qgroup2, qgroup3))

    occ_outer_pos = filtration.cl_occ_outer_pos.get()
    # divide by 2 because of the sampling of outer_pos
    assert occ_outer_pos[qgroup1 // 2] == 0
    assert occ_outer_pos[qgroup2 // 2] == 2

    occ_pos = filtration.cl_occ_pos.get()
    # two occurences of 0 qgrams, 1 occurence of 3, ...
    assert np.all(occ_pos == [0, 2, 3, 4, 5])

    occ = filtration.cl_occ.get()
    # query 0 and 1 have a 0 qgram, 0 has a 3 qgram, ...
    assert set(occ[:2]) == set([32, 1])
    assert np.all(occ[2:] == [0, 64, 33])


def test_filter_reference():
    cl_queries, cl_sizes = setup_queries()
    filtration = get_filtration()
    filtration.index(cl_queries, cl_sizes)

    cl_ref, cl_ref_pos, ref_size = setup_reference()
    cl_putative_positions, cl_putative_queries = filtration.filter(
        cl_ref, cl_ref_pos)
    putative_positions = cl_putative_positions.get()
    putative_queries = cl_putative_queries.get()
    # expecting 1 match for query 0 at 15, 1 match for query 1 at 16
    hits = np.vstack((putative_positions, putative_queries))
    assert set(map(tuple, hits.T)) == set([(15,0), (16,1)])


def test_map_queries():
    cl_ref, cl_ref_pos, ref_size = setup_reference()
    ref_offset = 0

    validation = get_validation()

    cl_queries, cl_sizes = setup_queries()
    cl_putative_positions, cl_putative_queries = setup_putative_mappings()

    (
        cl_mapping_positions,
        cl_mapping_scores,
        cl_query_hits_pos) = validation.validate(
        cl_ref, ref_size, ref_offset, cl_queries, cl_sizes,
        cl_putative_positions, cl_putative_queries)
    mapping_positions = cl_mapping_positions.get()
    mapping_scores = cl_mapping_scores.get()
    print(mapping_positions)
    print(mapping_scores)
    assert np.all(ref_size + ref_offset - 1 - mapping_positions == [1, 0])  # adjust mapping positions before comparing since we validate backwards
    assert np.all(mapping_scores == [94, 100])  # last query shall not map


def test_postprocess():
    cl_queries, cl_sizes = setup_queries(
        queries=np.array([
        list(bitencoding.bitencode(b"CTCCAGTTTCACACACAGA")[::-1]), # maps to 0 and 56
        list(bitencoding.bitencode(b"CTCATTCGCTGTTCACAAA")[::-1]) # maps to 19
        ], dtype=np.uint8),
        sizes=np.array([19, 16], dtype=np.int32))
    cl_ref, cl_pos, ref_size = setup_reference(ref=bitencoding.bitencode((b"CTCCAGCACACACAGAATACTCATTCGCTGTTCATTTTTTTTTTTTTTTTTTTTTTCTCCAGCACACACAGATTGTATTGTTTT")[::-1]))
    print(ref_size)

    queries = Queries(count=2, sizes=cl_sizes.get(), names=None, encoded=cl_queries.get(), sequences=None, qualities=None, maxsize=np.max(cl_sizes.get()))
    references = References(count=1, names="X", sizes=[ref_size], encoded=[cl_ref.get()], strand_sizes=np.array([ref_size], dtype=np.int32), offsets=np.array([0], dtype=np.int32), positions=[cl_pos.get()], global_size=6.5e9)

    def expected_mapq(score, *all_scores):
        weight = lambda s: math.exp(s - 100)
        return min(
            60,
            int(
                -10 * math.log10(1 - weight(score) / sum(map(weight, all_scores)))
            )
        )

    expected = [
        [[0, 56, 95, 95, expected_mapq(95, 95, 80)],
         [0, 0, 80, 80, expected_mapq(80, 95, 80)]],
        []
    ]
    print("EXPECTED", expected)
    # set min_score to zero so that it is ignored in postprocessing
    min_score = 0

    for strata in (1, 2, 3, 4):
        # positions should mimic backward validation
        positions = ref_size - np.array([0, 0, 56, 56], dtype=np.int32) - 1  # TODO look at -1 again
        print(positions)
        scores = np.array([80, 80, 95, 95], dtype=np.int32)
        hits = Hits(
            positions=[positions],
            scores=[scores],
            query_hits_pos=[np.array([0, 4, 4], dtype=np.int32)])  # no hit for second query

        for postprocessed_hits in postprocessing.postprocess_hits(queries, references, hits, min_score, SCORE_MATRIX, strata=strata, gap_open=1, gap_extend=1, accurate_mapq=True):
            cigars = np.asarray(postprocessed_hits.cigars)
            cigar_sizes = np.asarray(postprocessed_hits.cigar_sizes)
            cigar_address = np.asarray(postprocessed_hits.cigar_address)
            postprocessed_hits_address = postprocessed_hits.hits_address
            postprocessed_hits = postprocessed_hits.hits

            for i in range(len(cigar_address) - 1):
                cigar = cigars[cigar_address[i]:cigar_address[i+1], :][:cigar_sizes[i], :]
                assert np.all(cigar == [[0, 6], [1, 3], [0, 10]])

            print(np.asarray(postprocessed_hits[:postprocessed_hits_address[1]]), expected[0][:strata])
            # hits of first query
            assert np.all(np.asarray(postprocessed_hits[:postprocessed_hits_address[1]]) == expected[0][:strata])
            # no hits for second query
            assert postprocessed_hits_address[2] - postprocessed_hits_address[1] == 0


def test_big():
    k = 10000

    cl_queries, cl_sizes = setup_queries_big(k=k)
    filtration = get_filtration(blocksize=512)
    filtration.index(cl_queries, cl_sizes)
    assert filtration.cl_occ.shape == (k,)

    cl_ref, cl_ref_pos, ref_size = setup_reference()
    ref_offset = 0
    cl_putative_positions, cl_putative_queries = filtration.filter(
        cl_ref, cl_ref_pos)
    putative_positions = cl_putative_positions.get()
    putative_queries = cl_putative_queries.get()

    assert set(range(k)).issubset(putative_queries)
    assert np.all(putative_positions == 16)
    validation = get_validation()
    (
        cl_mapping_positions,
        cl_mapping_scores,
        cl_query_hits_pos) = validation.validate(
        cl_ref, ref_size, ref_offset, cl_queries, cl_sizes,
        cl_putative_positions, cl_putative_queries)
    mapping_scores = cl_mapping_scores.get()
    assert np.all(mapping_scores == 16)


def test_long_query():
    query = np.array([3430758536,    4269137,  336822291,  136546876,  575351986,
         124773676,          5], dtype=np.uint32)
    ref = query
    ref_pos = np.arange(len(query), dtype=np.int32)
    cl_ref, cl_ref_pos = cl.copy(ref), cl.copy(ref_pos)
    cl_queries = cl.copy(np.array([query], dtype=np.uint32))
    cl_sizes = cl.copy(np.array([112], dtype=np.int32))

    filtration = get_filtration()
    filtration.index(cl_queries, cl_sizes)

    cl_putative_positions, cl_putative_queries = filtration.filter(
        cl_ref, cl_ref_pos)
    assert np.all(cl_putative_positions == 0)
    assert np.all(cl_putative_queries == 0)
    assert len(cl_putative_positions) == 112 / 16


def setup_queries_big(
    k=100000,
    random_queries=False,
    alphabet=[b"A", b"C", b"G", b"T"]):
    if random_queries:
        bitencoded = np.array(
            [list(bitencoding.bitencode(b"".join(
                random.choice(alphabet) for _ in range(128)
                ))) for _ in range(k)],
            dtype=np.uint8)
    else:
        bitencoded = np.array([
            list(bitencoding.bitencode(b"A" * 128)),
            ] * k, dtype=np.uint8)
    queries = bitencoding.pack_sequences(bitencoded)
    queries_sizes = np.array([128] * k, dtype=np.int32)
    cl_queries = cl.copy(queries)
    cl_sizes = cl.copy(queries_sizes)
    return cl_queries, cl_sizes


def setup_queries(
    queries=np.array([
        list(bitencoding.bitencode(b"A" * 16 + b"T")[::-1]),
        list(bitencoding.bitencode(b"T" + b"A" * 16)[::-1]),
        list(bitencoding.bitencode(b"A" + b"G" * 16)[::-1]) # ignore last base (first base here)
        ], dtype=np.uint8),
    sizes=np.array([17, 17, 16], dtype=np.int32)):

    queries = bitencoding.pack_sequences(queries)
    queries_sizes = sizes
    cl_queries = cl.copy(queries)
    cl_sizes = cl.copy(queries_sizes)
    return cl_queries, cl_sizes


def setup_reference_big(n=48000000, alphabet=[b"A", b"C", b"G", b"T"]):
    ref = bitencoding.bitencode(b"".join(random.choice(alphabet) for _ in range(n)))
    ref_size = len(ref)
    ref = bitencoding.pack_sequences(np.array([list(ref)], dtype=np.uint8))[0]
    ref_pos = np.arange(math.ceil(n / 16), dtype=np.int32)
    cl_ref = cl.copy(ref)
    cl_ref_pos = cl.copy(ref_pos)
    return cl_ref, cl_ref_pos, ref_size


def setup_reference(ref=bitencoding.bitencode((b"T" + b"A" * 16 + b"G" * 16)[::-1])):
    ref_size = len(ref)
    ref = bitencoding.pack_sequences(np.array([list(ref)], dtype=np.uint8))[0]
    ref_pos = np.array([1], dtype=np.int32)
    cl_ref = cl.copy(ref)
    cl_ref_pos = cl.copy(ref_pos)
    return cl_ref, cl_ref_pos, ref_size


def setup_putative_mappings():
    # return two correctly mapping candidates and one false positive
    return (
        cl.copy(np.array([16] * 3, dtype=np.int32)),
        cl.copy(np.array([0, 1, 2], dtype=np.int32)))
