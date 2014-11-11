#!/usr/bin/env python3
"""
Compare two strings using global or semi-global alignment.
"""
from sqt import HelpfulArgumentParser
import sys
import os
from sqt.align import globalalign, GlobalAlignment
#, print_alignment #, SEMIGLOBAL, GLOBAL
from sqt.dna import reverse_complement

__author__ = "Marcel Martin"


def align_and_print(sequence1, sequence2, width, semiglobal):
	ga = GlobalAlignment(sequence1, sequence2, semiglobal=semiglobal)
	ga.print(width=width, gap_char='-')
	print()
	print('Length of sequence 1 (top):', len(sequence1))
	print('Length of sequence 2 (bottom):', len(sequence2))
	print('Errors in alignment:', ga.errors)
	print('Length of overlap in sequence 1:', ga.stop1 - ga.start1)
	print('Length of overlap in sequence 2:', ga.stop2 - ga.start2)
	#print('insert size:', front_length, '+', middle_length, '+', tail_length, '=', front_length + middle_length + tail_length)


def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	parser.add_argument('--semiglobal', action='store_true', default=False,
		help='Run a semi-global alignment (for detecting overlaps)')
	parser.add_argument('--reverse-complement', '--rc', action='store_true', default=False,
		help='Run the alignment also with the reverse-complement of the second sequence')
	parser.add_argument('sequence1')
	parser.add_argument('sequence2')
	return parser


def main():
	parser = get_argument_parser()
	args = parser.parse_args()

	sequence1 = args.sequence1.encode('ascii')
	sequence2 = args.sequence2.encode('ascii')

	# credit: http://stackoverflow.com/questions/566746/
	rows, columns = os.popen('stty size', 'r').read().split()
	columns = int(columns)

	print('Alignment:')
	print()
	align_and_print(sequence1, sequence2, columns, semiglobal=args.semiglobal)

	if args.reverse_complement:
		sequence2_rc = reverse_complement(sequence2)
		print()
		print("Alignment with reverse-complemented sequence 2:")
		print()
		align_and_print(sequence1, sequence2_rc, columns, semiglobal=args.semiglobal)


if __name__ == '__main__':
	main()
