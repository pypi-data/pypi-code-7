#!/usr/bin/env python3
"""
Print and optionally plot a read length histogram of FASTQ file.

TODO

- Multiple input FASTQ files are possible, but plotting doesn't work correctly then.
"""
import sys
from collections import Counter
from sqt.io.fasta import FastqReader
from sqt import HelpfulArgumentParser

__author__ = "Marcel Martin"


def fastq_length_histogram(path):
	"""Return read length histogram"""
	lengths = []
	with FastqReader(path) as reader:
		for record in reader:
			lengths.append(len(record.sequence))
	return lengths


def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	add = parser.add_argument
	add('--plot', default=None, help='Plot to this file (.pdf or .png)')
	add("--title", default='Read length histogram of {}',
		help="Plot title, {} is replaced with the input file name (default: '%(default)s')")
	#add('--detailed', '-d', default=False, action='store_true',
		#help='Print information about the sequences themselves, '
			#'such as the character distribution.')
	add('fastq', nargs='+', metavar='FASTQ',
		help='Input FASTQ file(s) (may be gzipped).')
	return parser


def main():
	parser = get_argument_parser()
	args = parser.parse_args()
	for path in args.fastq:
		print("## File:", path)
		print("length", "frequency", sep='\t')
		lengths = fastq_length_histogram(path)
		freqs = Counter(lengths)
		for length in range(0, max(freqs) + 1):
			freq = freqs[length]
			print(length, freq, sep='\t')
		if args.plot:
			import matplotlib.pyplot as plt
			import numpy as np
			lengths = np.array(lengths)
			histomax = int(np.percentile(lengths, 99.9) * 1.01)
			larger = sum(lengths > histomax)

			fig = plt.figure(figsize=(40/2.54, 20/2.54))
			ax = fig.gca()
			ax.set_xlabel('Read length')
			ax.set_ylabel('Frequency')
			ax.set_title(args.title.format(path))
			_, borders, _ = ax.hist(lengths, bins=100, range=(0, histomax))
			w = borders[1] - borders[0]
			ax.bar([histomax], [larger], width=w, color='red')
			ax.set_xlim(0, histomax + 1.5 * w)
			fig.savefig(args.plot)


if __name__ == '__main__':
	main()
