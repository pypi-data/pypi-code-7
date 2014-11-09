# -*- coding: utf-8 -*-


"""PEANUT (ParallEl AligNment UTility) is a massively parallel read mapper exploiting
the capabilities of modern GPUs. PEANUT requires an NVIDIA GPU with at least 2.5Gb of memory.
"""


__author__ = "Johannes Köster"
__license__ = "MIT"


import sys
import logging
import argparse
import re
import random
from collections import defaultdict, namedtuple
from functools import wraps
import queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from threading import Event
import signal
import traceback
import time

import numpy as np

from peanut.reference import read_references, write_references
from peanut.query import read_queries
import peanut.input
import peanut.output
from peanut.filtration import Filtration
from peanut.validation import Validation
from peanut.utils import CLDevice, PeanutError
import peanut.alignment as alignment
from peanut.stats import stats
import peanut.postprocessing as postprocessing
from peanut.version import __version__


SEED_INDEX = 4579
SEED_MAPPING = 908975


assert SEED_INDEX != SEED_MAPPING


QUEUE_SENTINEL = None
ERROR = Event()


SCORE_MATRIX = - np.ones((4,4), dtype=np.int32)
np.fill_diagonal(SCORE_MATRIX, 1)


Hits = namedtuple("Hits", "positions scores query_hits_pos")


class StopQueue(Exception):
    pass


class Queue(queue.Queue):
    def put(self, item):
        while not error():
            try:
                return super().put(item, timeout=2)
            except:
                pass
        raise StopQueue()

    def get(self):
        while not error():
            try:
                return super().get(timeout=2)
            except:
                pass
        return QUEUE_SENTINEL

    def wait_free(self):
        while not error():
            if not self.full():
                return
            time.sleep(1)


def error():
    """Return true if error occured."""
    return ERROR.is_set()


def error_handler(func):
    """Decorator for error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except StopQueue:
            pass
        except (BaseException, Exception) as e:
            #traceback.print_exc(file=sys.stderr)
            ERROR.set()
            raise e
    return wrapper


def term_handler(*args):
    """Handle termination on user request."""
    logging.info("Terminating PEANUT on user request.")
    ERROR.set()


signal.signal(signal.SIGINT, term_handler)


def create_index(
    referencepath,
    indexpath,
    cpu=False,
    min_repeat_count=1000,
    blocksize=512,
    statspath=None):
    """Create a PEANUT index for the given reference."""

    cldevice = CLDevice(cpu=cpu)
    stats.cl = cldevice
    random.seed(SEED_INDEX)
    filtration = Filtration(cldevice=cldevice, blocksize=blocksize)
    with peanut.input.open_hdf5(indexpath, write=True) as index:
        write_references(index, referencepath, filtration, min_repeat_count=min_repeat_count)

    if statspath is not None:
        stats.write(statspath)


@error_handler
def map_queries(
    queriespath,
    indexpath,
    matespath=None,
    min_score=40,
    strata=-1,
    accurate_mapq=False,
    skip_alignment=False,
    max_hits=100,
    semiglobal_alignment=False,
    gap_open_penalty=6,
    gap_extend_penalty=1,
    blocksize_filtration=512,
    blocksize_validation=512,
    query_buffersize=1000000,
    postprocessing_buffersize=100000,
    cpu=False,
    statspath=None,
    no_output=False,
    threads=1,
    read_group=[],
    use_xa=False,
    paired=False,
    insert_size=220,
    insert_size_error=50):
    """Map given queries to reference."""

    random.seed(SEED_MAPPING)

    with peanut.input.open_hdf5(indexpath) as hdf5file, ThreadPoolExecutor(max_workers=3) as pool:
        hit_queue = Queue(maxsize=1)
        bam_queue = Queue(maxsize=1)
        references = read_references(hdf5file)

        postprocessing_future = pool.submit(
            _postprocess_hits, hit_queue, bam_queue,
            references, min_score, strata=strata, max_hits=max_hits,
            gap_open_penalty=gap_open_penalty,
            gap_extend_penalty=gap_extend_penalty,
            semiglobal_alignment=semiglobal_alignment, threads=threads,
            buffersize=postprocessing_buffersize, paired=paired,
            insert_size=insert_size, insert_size_error=insert_size_error,
            accurate_mapq=accurate_mapq,
            skip_alignment=skip_alignment)

        writing_future = pool.submit(
            _write_hits, bam_queue, references, read_group, paired=paired,
            use_xa=use_xa, no_cigars=skip_alignment) if not no_output else pool.submit(eat_queue, bam_queue)

        stats.start_timer("overall_running_time")

        _map_queries(
            hit_queue, references, queriespath, matespath=matespath,
            cpu=cpu, blocksize_filtration=blocksize_filtration, query_buffersize=query_buffersize,
            blocksize_validation=blocksize_validation, min_score=min_score)

        writing_future.result()
        postprocessing_future.result()

    stats.stop_timer("overall_running_time")
    if statspath is not None:
        stats.write(statspath)


@error_handler
def eat_queue(queue):
    """Dummy function to terminate queue."""
    while not error():
        item = queue.get()
        if item is QUEUE_SENTINEL:
            queue.task_done()
            return
        queue.task_done()


@error_handler
def _map_queries(
    hit_queue,
    references,
    queriespath,
    matespath=None,
    cpu=False,
    query_buffersize=1000000,
    blocksize_filtration=512,
    blocksize_validation=512,
    min_score=40):
    """Worker for mapping queries."""

    cl = CLDevice(cpu=cpu)
    stats.cl = cl

    filtration = Filtration(cldevice=cl, blocksize=blocksize_filtration)
    validation = Validation(cldevice=cl, blocksize=blocksize_validation,
        min_score=min_score)

    stats.start_timer("overall_mapping_running_time")
    processed = 0
    for queries in read_queries(
            queriespath,
            matespath=matespath,
            buffersize=query_buffersize):
        logging.info("buffered {} queries".format(len(queries.names)))

        processed += queries.count

        logging.debug("filtration and validation")

        cl_queries = cl.copy(queries.encoded)
        cl_queries_sizes = cl.copy(queries.sizes)

        stats.start_timer("index_running_time")
        filtration.index(cl_queries, cl_queries_sizes)
        stats.stop_timer("index_running_time")

        hit_positions = list()
        hit_scores = list()
        query_hits_pos = list()

        def map_to_ref(refid, reference_encoded, reference_pos, reference_size, reference_offset):
            #logging.info("copy reference")
            cl_reference = cl.copy(reference_encoded)
            cl_reference_pos = cl.copy(reference_pos)

            # filter reference and generate putative mappings
            stats.start_timer("filtration_running_time")
            cl_hit_positions, cl_hit_queries = filtration.filter(
                cl_reference, cl_reference_pos)
            stats.stop_timer("filtration_running_time")

            # check putative mappings by bitparallel alignment
            stats.start_timer("validation_running_time")
            (cl_hit_positions,
                cl_hit_scores, cl_query_hits_pos) = validation.validate(
                    cl_reference, reference_size, reference_offset, cl_queries,
                    cl_queries_sizes, cl_hit_positions, cl_hit_queries)
            stats.stop_timer("validation_running_time")

            # postprocess hits
            hit_positions.append(cl_hit_positions.get())
            hit_scores.append(cl_hit_scores.get())
            query_hits_pos.append(cl_query_hits_pos.get())

            del cl_hit_positions
            del cl_hit_scores
            del cl_query_hits_pos
            del cl_hit_queries
            del cl_reference
            del cl_reference_pos
            cl.pool.free_held()

        stats.start_timer("plain_mapping_running_time")
        for refid, ref in enumerate(zip(references.encoded, references.positions, references.strand_sizes, references.offsets)):
            if error():
                break
            logging.debug("{} strand of {}".format(
                "reverse" if refid % 2 else "forward",
                peanut.output.strip_fasta_comment(references.names[refid // 2]).decode()))
            map_to_ref(refid, *ref)
        stats.stop_timer("plain_mapping_running_time")

        hit_queue.put((queries, Hits(hit_positions, hit_scores, query_hits_pos)))
        logging.debug("hit queue: {} items".format(hit_queue.qsize()))

        del cl_queries
        del cl_queries_sizes
        filtration.cleanup()
        cl.pool.free_held()
        logging.info("filtered and validated hits of {} queries".format(processed))

        # wait for postprocessing to be finished
        hit_queue.wait_free()
    hit_queue.put(QUEUE_SENTINEL)
    stats.stop_timer("overall_mapping_running_time")


@error_handler
def _postprocess_hits(
    hit_queue,
    bam_queue,
    references,
    min_score,
    score_matrix=SCORE_MATRIX,
    strata=-1,
    max_hits=100,
    semiglobal_alignment=False,
    gap_open_penalty=6,
    gap_extend_penalty=1,
    threads=1,
    buffersize=100000,
    paired=False,
    insert_size=220,
    insert_size_error=50,
    accurate_mapq=False,
    skip_alignment=False):
    """Worker for postprocessing."""

    processed = 0
    while True:
        item = hit_queue.get()
        if item is QUEUE_SENTINEL:
            hit_queue.task_done()
            bam_queue.put(QUEUE_SENTINEL)
            return
        queries, hits = item

        logging.debug("postprocessing")
        stats.start_timer("postprocessing")
        for postprocessed_hits in postprocessing.postprocess_hits(
            queries, references, hits, min_score,
            score_matrix, gap_open=gap_open_penalty,
            gap_extend=gap_extend_penalty,
            semiglobal_alignment=semiglobal_alignment,
            strata=strata, max_hits=max_hits,
            threads=threads, buffersize=buffersize,
            paired=paired, insert_size=insert_size,
            insert_size_error=insert_size_error,
            accurate_mapq=accurate_mapq,
            skip_alignment=skip_alignment):
            bam_queue.put((queries, postprocessed_hits))
            logging.debug("bam queue: {} items".format(bam_queue.qsize()))
        stats.stop_timer("postprocessing")
        hit_queue.task_done()
        processed += queries.count
        logging.info("postprocessed hits of {} queries".format(processed))


@error_handler
def _write_hits(
    bam_queue,
    references,
    read_group,
    paired=False,
    use_xa=False,
    no_cigars=False
    ):
    """Worker for writing."""

    processed = 0
    peanut.output.print_sam_header(references, read_group)
    while True:
        item = bam_queue.get()
        if item == QUEUE_SENTINEL:
            logging.debug("terminated bam writing")
            return
        logging.debug("writing")
        queries, postprocessed_hits = item
        stats.start_timer("writing")
        peanut.output.print_sam(queries, postprocessed_hits, paired, references.names, use_xa, no_cigars=no_cigars)
        processed += postprocessed_hits.window_size
        del postprocessed_hits
        stats.stop_timer("writing")
        bam_queue.task_done()
        logging.info("written hits of {} queries".format(processed))


def argument_parser():
    """Setup the CLI argument parser."""
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_argument_group("technical parameters")
    group.add_argument("--profile", metavar="PATH", help="Activate profiling and write profile into FILE. Requires yappi.")
    group.add_argument("--stats", metavar="PATH", help="Path to write stat data.")
    group.add_argument("--debug", action="store_true", help="Print debugging output.")
    group.add_argument("--cpu", action="store_true", help="Use CPU.")

    group = p.add_argument_group("sub commands")
    subparsers = p.add_subparsers(dest="subcommand", title="commands", help='The functionality to execute.')

    index = subparsers.add_parser("index",
        help="Index a reference for faster access.")

    group = index.add_argument_group("files")
    group.add_argument("reference",
        help="The reference to map to as .fasta file.")
    group.add_argument("index",
        help="Index file to create as .hdf5 file.")

    group = index.add_argument_group("sensitivity parameters")
    group.add_argument("--min-repeat-count", "-r", type=int, metavar="N", default=2500,
        help="Minimal number of occurences at which a qgram is "
        "marked as repetetive and ignored. For the human reference genome, "
        "this should be set to 2500 for a good sensitivity/speed ratio (default 2500).")

    mapping = subparsers.add_parser("map", help="Perform the mapping.")

    group = mapping.add_argument_group("files")
    group.add_argument("reference", help="Path to indexed reference sequences as HDF5 or, alternatively path to reference fasta. In the latter case, the index is expected at path/to/ref.hdf5 if path/to/ref.fasta is the given reference.")
    group.add_argument("queries",
        help="Sequences to map as FASTA "
            "or FASTQ files (i.e. sequence reads).")
    group.add_argument("mates", nargs="?",
        help="Mate-pair or paired-end sequences to map as FASTA or FASTQ files.")

    group = mapping.add_argument_group("input file parameters")
    group.add_argument("--paired", "-p", action="store_true", help="Assume first input is interleaved fastq file.")

    group = mapping.add_argument_group("execution parameters")
    group.add_argument("--threads", type=int, default=1, metavar="N", help="CPU-Threads for postprocessing and alignment (default 1).")
    group.add_argument("--query-buffer", "--read-buffer", "-b", metavar="N", type=int, default=1000000, help="How many queries (reads) should be mapped in parallel (default 1000000).")
    group.add_argument("--postprocessing-buffer", "--pb", type=int, metavar="N", help="How many queries should be postprocessed in parallel (per default the same as --query-buffer).")

    group = mapping.add_argument_group("sensitivity parameters")
    group.add_argument("--semiglobal", "-S", action="store_true", help="Calculate a semi-global instead of local alignment.")
    group.add_argument("--percent-identity", "-i", type=int, default=80, metavar="N", help="Minimum percent identity for mapping to a position. This is the fraction of matches in the alignment starting at the mapping position (default 80).")
    group.add_argument("--strata", "-s", default=1, metavar="N", help="How many strata (hits of the same quality) should be reported for each read (default: 1). Use --strata all to report all strata.")
    group.add_argument("--max-hits", "-m", type=int, default=100, metavar="N", help="Maximum number of hits per read (default 100). Regardless of strata value, this limits the number of records per read in the bam file.")
    group.add_argument("--accurate-mapq", action="store_true", help="Do not set all mapping qualities to zero if a read aligns ambiguously to multiple positions. The default behaviour ensures compatibility to downstream tools like GATK.")
    group.add_argument("--insert-size", "--isize", type=int, default=300, metavar="I", help="Expected insert size for read and mate (default 300). See --insert-size-error for effects.")
    group.add_argument("--insert-size-error", "--ierr", type=int, default=300, metavar="E", help="Maximum deviation from expected insert size (default 300). Insert sizes within [I-Em, I+E] will lead to read and mate being marked as properly paired. Note: if this interval is improper for your data, it can lead to slowdowns because the rescue mode becomes active for unpaired reads.")
    group.add_argument("--gap-open-penalty", "-O", default=2, type=int, metavar="N", help="Gap open penalty (default 2).")
    group.add_argument("--gap-extend-penalty", "-E", default=1, type=int, metavar="N", help="Gap extend penalty (default 1).")

    group = mapping.add_argument_group("output format parameters")
    group.add_argument("--read-group", "--rgid", nargs="+", metavar="ENTRY", help="The read group (e.g. --read-group ID:XY SM:21347 PL:Illumina). At least ID is required.")
    group.add_argument("--no-xa", action="store_true", help="Do not use the XA tag for reporting alternative alignments (this can lead to larger output and increased running time).")
    group.add_argument("--no-alignments", action="store_true", help="Do not report the actual alignments. This omits the calculation of the CIGAR strings and therefore saves a lot of time.")

    group = mapping.add_argument_group("technical parameters")
    group.add_argument("--blocksize-filtration", "--bf", type=int, default=512, metavar="N",
        help="Work group size of filtration OpenCL kernels (default 512).")
    group.add_argument("--blocksize-validation", "--bv", type=int, default=448, metavar="N",
        help="Work group size of validation OpenCL kernel (default 448).")
    return p


def main(profile=False):
    """Run PEANUT."""
    parser = argument_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format=" %(asctime)s: %(message)s", level=log_level, stream=sys.stderr)

    if args.profile:
        import yappi
        yappi.start()

    try:
        if args.subcommand == "index":
            create_index(
                args.reference,
                args.index,
                min_repeat_count=args.min_repeat_count,
                statspath=args.stats,
                cpu=args.cpu)
        elif args.subcommand == "map":

            if args.read_group:
                if not any(item.startswith("ID:") for item in read_group):
                    print("An ID field is required if read group is specified.", file=sys.stderr)
                    exit(1)

            if args.strata == "all":
                strata = -1
            else:
                try:
                    strata = int(args.strata)
                    if strata <= 0:
                        raise ValueError()
                except ValueError:
                    print("Strata must be either all or a positive number.", file=sys.stderr)
                    exit(1)

            query_buffer = args.query_buffer
            paired = args.paired or args.mates
            if paired and query_buffer % 2:
                query_buffer += 1

            postprocessing_buffer = query_buffer if args.postprocessing_buffer is None else args.postprocessing_buffer

            if args.reference.endswith("hdf5"):
                index = args.reference
            else:
                index = re.sub("(\.fasta\.gz|\.fasta)$", ".hdf5", args.reference)

            map_queries(
                args.queries,
                index,
                matespath=args.mates,
                min_score=args.percent_identity,
                strata=strata,
                accurate_mapq=args.accurate_mapq,
                skip_alignment=args.no_alignments,
                max_hits=args.max_hits,
                semiglobal_alignment=args.semiglobal,
                gap_open_penalty=args.gap_open_penalty,
                gap_extend_penalty=args.gap_extend_penalty,
                blocksize_filtration=args.blocksize_filtration,
                blocksize_validation=args.blocksize_validation,
                query_buffersize=query_buffer,
                postprocessing_buffersize=postprocessing_buffer,
                statspath=args.stats,
                threads=args.threads,
                read_group=args.read_group,
                use_xa=not args.no_xa,
                cpu=args.cpu,
                paired=paired,
                insert_size=args.insert_size,
                insert_size_error=args.insert_size_error)
        else:
            parser.print_help()
    except PeanutError as e:
        print(e, file=sys.stderr)
        exit(1)

    if args.profile:
        with open(args.profile, "w") as out:
            profile = yappi.get_func_stats()
            profile.sort("totaltime")
            profile.print_all(out=out)
    exit(0)
