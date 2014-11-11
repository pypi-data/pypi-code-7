#!/usr/bin/env python3
# kate: word-wrap-column 80; word-wrap off;
"""
Print a report about a SAM/BAM file.
"""
__author__ = 'Marcel Martin'

import sys
from collections import Counter, namedtuple, defaultdict
from itertools import islice
from contextlib import ExitStack
from pysam import Samfile
from sqt import HelpfulArgumentParser, Cigar, cigar


Subalignment = namedtuple("Subalignment", ['length', 'pos', 'tid'])

class SupplementaryAlignment(namedtuple("SupplementaryAlignment",
	['rname', 'pos', 'strand', 'cigar', 'mapq', 'edit_distance'])):

	@property
	def qstart(self):
		return soft_clipping_length(self.cigar, 0)

	@property
	def qend(self):
		return soft_clipping_length(self.cigar, 0) + cigar.aligned_bases(self.cigar)


def header(s):
	print(s)
	print('-' * len(s))
	print()


def soft_clipping_length(cig, where):
	"""
	Return length of soft-clipping at the ends of an alignment.

	where -- 0 stands for the beginning of alignment, -1 for the end.
	"""
	assert where in (0, -1)
	if not cig:
		return 0
	p = cig[where]
	if p[0] == cigar.S:
		return p[1]
	return 0


def parse_supplementary(sa):
	"""
	Parse supplementary alignments given by the SA:Z: tag in a SAM record.

	Return a list of SupplementaryAlignment objects.
	"""
	fields = sa.split(';')
	assert fields[-1] == ''  # sa must end with a ';'
	alignments = []
	for field in fields[:-1]:
		ref, pos, strand, cig, mapq, edit_dist = field.split(',')
		pos = int(pos) - 1
		cig = Cigar.parse(cig)  # TODO should be Cigar(cig)
		mapq = int(mapq)
		edit_dist = int(edit_dist)
		assert strand in '+-'
		a = SupplementaryAlignment(ref, pos, strand, cig, mapq, edit_dist)
		alignments.append(a)
	return alignments


def overall_aligned_bases(read, rname, report=None, minimum_cover_fraction=0.01):
	"""
	Given an AlignedRead that potentially has supplementary alignments
	specified by the SA tag, return how many of its bases are aligned,
	considering all supplementary alignments.

	report -- a file-like object to which a report is written for this read.
	"""
	tags = dict(read.tags)
	alignments = [SupplementaryAlignment(rname, read.pos, '+-'[int(read.is_reverse)],
		read.cigar, read.mapq, tags['NM'])]
	if 'SA' in tags:
		alignments.extend(parse_supplementary(tags['SA']))

	if report is not None:
		read_length = Cigar(read.cigar).query_length(count_clipped='hard')
		print('Read {} ({:.1f}kbp):'.format(read.qname, read_length / 1000), file=report)
		for alignment in sorted(alignments, key=lambda a: (a.qstart, a.qend)):
			cigar = Cigar(alignment.cigar)
			alignment_length = cigar.query_length(count_clipped=None)
			if alignment_length / read_length < minimum_cover_fraction:
				continue
			rstop = alignment.pos + cigar.reference_length()
			print(
				'{:9} bp'.format(alignment_length),
				'{:6.1%}'.format(alignment_length / read_length),
				'{:6} ... {:6}  '.format(alignment.qstart+1, alignment.qend),
				'{} {:>2}:{}-{}'.format(alignment.strand,
					alignment.rname, alignment.pos+1, rstop),
				file=report)

	events = []
	for alignment in alignments:
		events.append((alignment.qstart, 'start', None))
		events.append((alignment.qend, 'stop', alignment))

	depth = 0  # number of observed 'start' events
	bases = 0  # number of covered bases
	last_qstart = None
	for qpos, what, alignment in sorted(events, key=lambda x: x[0]):
		if what == 'start':
			if depth == 0:
				last_qstart = qpos
			depth += 1
		elif what == 'stop':
			depth -= 1
			if depth == 0:
				# interval (last_qstart, qpos) was covered
				bases += qpos - last_qstart
	if report is not None:
		print('{:.1%} aligned ({}/{})\n'.format(bases / read_length,
			bases, read_length),
			file=report)
	return bases


def print_basics(alignments, lengths, aligned_bases):
	header('Basic statistics')
	bases = sum(lengths.values())
	total_reads = len(lengths)
	mapped_reads = len(alignments)
	total_alignments = sum(len(a) for a in alignments.values())
	print('Number of reads:     {:10,d}'.format(total_reads))
	print('unfiltered+CIGAR:    {:10,d} ({:.2%})'.format(mapped_reads, mapped_reads / total_reads))
	print('Alignments per read: {:.3f} (only mapped reads)'.format(total_alignments / total_reads))  # TODO is this correct?
	print('bases:         {:15,d} ({:.2f} Gbp)'.format(bases, bases / 1E9))
	print('aligned bases: {:15,d} ({:.2f} Gbp) ({:.2%})'.format(aligned_bases, aligned_bases/1E9, aligned_bases/bases))
	print()


def print_subalignment_histogram(number_alignments):
	print('Histogram of number of subalignments')
	rest = 0
	for number, count in number_alignments.items():
		if number <= 10:
			print(' {:2} {:9}'.format(number, count))
		else:
			rest += count
	if rest > 0:
		print('>10 {:9}'.format(rest))
	print()


def print_subalignment_stats(reads, read_lengths, refnames_map):
	header('Subalignment statistics')
	total_reads = len(read_lengths)
	fully_aligned_95 = 0  # reads whose bases are 95% aligned within one subalignment
	fully_aligned_99 = 0  # reads whose bases are 99% aligned within one subalignment
	number_alignments = Counter()
	interesting = 0
	for name, alignments in reads.items():
		lengths = [ alignment.length for alignment in alignments ]
		refnames = [ refnames_map[alignment.tid] for alignment in alignments ]
		rl = read_lengths[name]

		#print(name.rjust(40), read_lengths[name], lengths, sum(lengths), ', '.join(refnames), end=' ')
		if len(lengths) >= 1 and lengths[0] >= 0.95 * rl:
			fully_aligned_95 += 1
		if len(lengths) >= 1 and lengths[0] >= 0.99 * rl:
			fully_aligned_99 += 1
		number_alignments[len(lengths)] += 1

		# is this an 'interesting' read? (arbitrary thresholds)
		if 2 <= len(lengths) <= 4 and len(set(refnames)) > 1:
			interesting += 1

	print_subalignment_histogram(number_alignments)
	print('fully aligned (95%):{:10,d} ({:.2%})'.format(fully_aligned_95, fully_aligned_95/total_reads))
	print('fully aligned (99%):{:10,d} ({:.2%})'.format(fully_aligned_99, fully_aligned_99/total_reads))
	print('no of interesting reads:', interesting)
	print()


def print_cigar_usage(counter):
	header("CIGAR operator usage")
	total_ops = sum(counter.values())
	ops = 'MIDNSHPX='
	for op_i, op in enumerate(ops):
		print("{:2} {:14,d} ({:7.2%})".format(op, counter[op_i], counter[op_i]/total_ops))
	print()


def print_reference_usage(reflengths, reference_hits, minimum_reference_length=1000):
	header('Scaffold/chromosome/references usage')

	long_refs = sum(1 for length in reflengths if length >= minimum_reference_length)
	ref_hits_length = sum(reflengths[tid] for tid in reference_hits)
	total_ref_length = sum(reflengths)

	print('total length of references: {:,d} ({:.2f} Gbp)'.format(total_ref_length, total_ref_length/1E9))
	print('references:', len(reflengths))
	print('references hit by at least one alignment:', len(reference_hits))
	print('length of those references: {:,d} ({:.2%})'.format(ref_hits_length, ref_hits_length/total_ref_length))
	print('length of references not hit: {:,d}'.format(total_ref_length - ref_hits_length))
	#_refs = infile.references
	#assert infile.nreferences == len(_refs)
	#refname_to_length = dict(zip(_refs, infile.lengths))
	#for i in range(infile.nreferences):
		#assert refname_to_length[infile.getrname(i)] == reflengths[i]

	long_ref_hits = sum(1 for tid in reference_hits if reflengths[tid] >= minimum_reference_length)
	ref_hits_length = sum(reflengths[tid] for tid in reference_hits)
	print('references >= {} bp:'.format(minimum_reference_length), long_refs)
	print('references >= {} bp hit by at least one alignment:'.format(minimum_reference_length), long_ref_hits)


def main():
	parser = HelpfulArgumentParser(description=__doc__)
	parser.add_argument('--quality', '-q', type=int, default=0,
		help='Minimum mapping quality (default: %(default)s')
	parser.add_argument('--minimum-reference-length', metavar='N', type=int, default=0,
		help='For reference usage statistics, ignore references shorter than N.')
	parser.add_argument('--limit', metavar='N', type=int, default=None,
		help='Process only the first N entries in the input file.')
	parser.add_argument('--cover', metavar='FILE', default=None,
		help='Print report about "read coverage" (which sections are aligned) to FILE')
	parser.add_argument('--minimum-cover-fraction', metavar='FRACTION', type=float, default=0.01,
		help='Alignment must cover at least FRACTION of the read to appear in the cover report. (%(default)s)')
	parser.add_argument("bam", metavar="SAM/BAM", help="Name of a SAM or BAM file")
	args = parser.parse_args()

	# Count how often each CIGAR operator occurs
	cigar_counter = Counter()

	#
	read_lengths = defaultdict(int)
	reference_hits = defaultdict(int)
	bases = 0
	aligned_bases = 0
	alignments = defaultdict(list)  # maps a read name to a list of Subalignment objects
	n_records = 0
	unmapped = 0
	unmapped_bases = 0
	with ExitStack() as stack:
		sf = stack.enter_context(Samfile(args.bam))
		if args.cover is not None:
			cover = stack.enter_context(open(args.cover, 'wt'))
		else:
			cover = None
		for record in islice(sf, 0, args.limit):
			n_records += 1
			if record.is_unmapped:
				unmapped += 1
				unmapped_bases += len(record.seq)
				continue
			if record.mapq < args.quality:
				continue
			assert record.cigar is not None
			for op_i, l in record.cigar:
				cigar_counter[op_i] += l

# TODO
# - introduce a Read class with attributes length, alignments

			if record.qname not in read_lengths:
				aligned_bases += overall_aligned_bases(record, sf.getrname(record.tid), cover, args.minimum_cover_fraction)
				read_lengths[record.qname] = Cigar(record.cigar).query_length(
					count_clipped='hard')

			#assert record.qend - record.qstart == record.qlen == len(record.query)
			#assert record.alen == record.aend - record.pos
			#assert record.rlen == len(record.seq)

			reference_hits[record.tid] += 1
			#read_lengths[record.qname] = max(read_lengths[record.qname], record.rlen)
			alignments[record.qname].append(Subalignment(length=record.qlen, pos=record.pos, tid=record.tid))

		reflengths = sf.lengths
		nreferences = sf.nreferences
		assert nreferences == len(reflengths)
		refnames_map = { tid: sf.getrname(tid) for tid in range(nreferences) }


	assert len(read_lengths) == len(alignments)
	header('All entries in input file')
	print('Total entries:   {:10,d}'.format(n_records))
	print('Unmapped:        {:10,d}'.format(unmapped))
	print('Unmapped bases:  {:10,d}'.format(unmapped_bases))
	print()

	print_basics(alignments, read_lengths, aligned_bases)
	print_subalignment_stats(alignments, read_lengths, refnames_map)
	print_cigar_usage(cigar_counter)
	print_reference_usage(reflengths, reference_hits, minimum_reference_length=args.minimum_reference_length)


if __name__ == '__main__':
	main()



"""
Old code that used to be in bamstats:

parser.add_argument('--minimum-start', '-m', type=int, default=1,
	help='minimum start position (1-based). Reads starting earlier are ignored.')
parser.add_argument('--maximum-start', '-M', type=int, default=1E100,
	help='maximum start position (1-based). Reads starting later are ignored.')
parser.add_argument('--forward', action='store_true', default=False,
	help='count only reads mapped forward')


for read in samfile:
	if not (args.minimum_start <= read.pos + 1 <= args.maximum_start):
		continue
	counter[read.rname] += 1

	# TODO should qlen or alen be used?
	# qlen: no. of aligned bases in the read
	# alen: no. of aligned bases in the reference
	coverage[read.rname] += read.qlen
reference_names = samfile.references

for index, name in enumerate(reference_names):
	print(name, counter[index], coverage[index], sep='\t')
"""
