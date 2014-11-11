#!/usr/bin/env python3
"""

"""
__author__ = 'Marcel Martin'

import sys
from collections import Counter
from sqt import HelpfulArgumentParser
from pysam import Samfile


def main():
	parser = HelpfulArgumentParser(description=__doc__)
#	parser.add_argument('--sorted', '-s', action='store_true', default=False)
	parser.add_argument('--quality', '-q', type=int, default=-1000,
		help='minimum mapping quality')
	parser.add_argument('--minimum-start', '-m', type=int, default=1,
		help='minimum start position (1-based). Reads starting earlier are ignored.')
	parser.add_argument('--maximum-start', '-M', type=int, default=1E100,
		help='maximum start position (1-based). Reads starting later are ignored.')
	parser.add_argument('--forward', action='store_true', default=False,
		help='count only reads mapped forward')
	parser.add_argument("bam", metavar="SAM/BAM", help="name of a SAM or BAM file")
	args = parser.parse_args()

	allexpressions = []
	counter = Counter()
	coverage = Counter()
	with Samfile(args.bam) as samfile:
		for read in samfile:
			if read.mapq < args.quality or read.is_unmapped:
				continue
			if args.forward and read.is_reverse:
				continue
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

if __name__ == '__main__':
	main()
