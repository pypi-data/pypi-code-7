#!/usr/bin/env python3
"""
Modify FASTA and FASTQ files by picking subsets and modifying individual entries.

Possible modifications:
- Pick a subset of records (given by name). With lots of names, this is faster
  than 'grep -A 3 --no-group-separator -f readnames.txt file.fastq' magic, which
  may be used with FASTQ files.
  If the record name ends in '/1' or '/2', these two charecter are ignored when
  comparing to the names in the file.
- Trim low-quality ends
- Trim reads to a given length
- Discard reads shorter than a given length
- Discard reads in which the expected number of errors exceeds a threshold
- Reverse-complement each read
- Convert from FASTA to FASTQ by assigning a fixed quality value to all bases
- Convert from FASTQ to FASTA by dropping all quality values
- Make read names unique

Modifications are done in the order in which they are listed above.
The result is written to standard output.

The algorithm for quality trimming is the same as the one used by BWA:
- Subtract the cutoff value from all qualities.
- Compute partial sums from all indices to the end of the sequence.
- Trim sequence at the index at which the sum is minimal.
"""
import sys
import errno
from collections import defaultdict
from sqt import HelpfulArgumentParser, SequenceReader, FastaWriter, FastqWriter
from sqt.dna import reverse_complement
from sqt.qualtrim import quality_trim_index as trim_index, expected_errors

__author__ = "Marcel Martin"


def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	arg = parser.add_argument
	arg('--names', metavar='FILE', default=None,
		help='Keep only those records whose names occur in FILE (one per line)')
	arg("-q", "--cutoff", type=int, default=None,
		help="Quality cutoff. Only when input format is FASTQ")
	arg("--length", "-l", type=int, default=None,
		help="Shorten records to LENGTH (default: do not shorten)")
	arg('-m', '--minimum-length', type=int, default=0, metavar='LENGTH',
		help='Discard reads shorter than LENGTH')
	arg('--max-errors', type=float, default=None, metavar='X',
		help='Discard reads whose expected number of errors (computed '
			'from quality values) exceeds X.')
	arg('--reverse-complement', '-r', action='store_true',
		default=False, help='Reverse-complement each sequence')
	arg('--constant-quality', '-c', metavar='QUALITY', type=int, default=None,
		help='Set all quality values to QUALITY. Use this to convert from '
			'FASTA to FASTQ.')
	arg('--fasta', default=False, action='store_true',
		help='Always output FASTA (drop qualities if input is FASTQ)')
	arg('--unique-names', action='store_true', default=False,
		help="Make record names unique by appending _1, _2 etc. when necessary")

	arg("--width", "-w", type=int, default=80,
		help="Characters per line in output FASTA (default: %(default)s). "
			"Set to 0 to disallow line breaks entirely. This is ignored for FASTQ files.")
	arg('path', metavar='FASTA/FASTQ',
		help='input FASTA or FASTQ file')
	"""
	Some possible extensions to this tool:

	arg("--histogram", action="store_true", default=False,
		help="Print a histogram of the length of removed ends")
	arg("-c", "--colorspace", action="store_true", default=False,
		help="Assume input files are in color space and that the sequences contain an initial primer base")
	arg("-z", "--clip-qualities", action="store_true", default=False,
		help="Replace negative qualities with 0. Assumes qualities are stored as chr(qual+33).")
	arg("-n", "--limit", type=int, default=None,
		help="Limit output to N reads (discarding the rest) (default: no limit).")
	"""
	return parser


class ReadPicker:
	def __init__(self, file_with_names):
		read_names = []
		with open(file_with_names) as f:
			read_names = f.read().split('\n')
		self.read_names = { rn for rn in read_names if rn != '' }

	def __call__(self, read):
		rname = read.name.split(' ', maxsplit=1)[0]
		if rname.endswith('/1'):
			rname = rname[:-2]
		elif rname.endswith('/2'):
			rname = rname[:-2]
		if rname in self.read_names:
			return read
		else:
			return None


class QualityTrimmer:
	def __init__(self, cutoff):
		self.cutoff = cutoff

	def __call__(self, read):
		index = trim_index(read.qualities, self.cutoff)
		return read[:index]


class Shortener:
	def __init__(self, length):
		self.length = length

	def __call__(self, read):
		return read[:self.length]


class MinimumLengthFilter:
	def __init__(self, length):
		self.minimum_length = length

	def __call__(self, read):
		if len(read) < self.minimum_length:
			return None
		else:
			return read


class MaxExpectedErrorFilter:
	"""
	Discard reads whose expected number of errors, according to the quality
	values, exceeds the given threshold.

	The idea comes from usearch's -fastq_maxee parameter
	(http://drive5.com/usearch/).
	"""
	def __init__(self, max_errors):
		self.max_errors = max_errors

	def __call__(self, read):
		if expected_errors(read.qualities) > self.max_errors:
			return None
		else:
			return read


def reverse_complementer(read):
	read.sequence = reverse_complement(read.sequence)
	if read.qualities:
		read.qualities = read.qualities[::-1]
	return read


class QualitySetter:
	def __init__(self, value):
		self.quality_char = chr(33 + value)

	def __call__(self, read):
		read.qualities = self.quality_char * len(read)
		return read


def quality_dropper(read):
	read.qualities = None
	return read


class UniqueNamer:
	def __init__(self):
		# Counter for occurrences of a name
		self.names = defaultdict(int)

	def __call__(self, read):
		if ' ' in read.name:
			name, description = read.name.split(' ', maxsplit=1)
		else:
			name = read.name
			description = None
		self.names[name] += 1
		if self.names[name] == 1:
			# Read not previously seen
			return read
		name = '{}_{}'.format(name, self.names[name] - 1)
		read.name = name
		if description is not None:
			read.name += ' ' + description
		return read


def main():
	parser = get_argument_parser()
	args = parser.parse_args()
	if args.width == 0:
		args.width = None

	modifiers = []
	if args.names:
		modifiers.append(ReadPicker(args.names))
	if args.cutoff is not None:
		modifiers.append(QualityTrimmer(args.cutoff))
	if args.length:
		modifiers.append(Shortener(args.length))
	if args.minimum_length != 0:
		modifiers.append(MinimumLengthFilter(args.minimum_length))
	if args.max_errors is not None:
		modifiers.append(MaxExpectedErrorFilter(args.max_errors))
	if args.reverse_complement:
		modifiers.append(reverse_complementer)
	if args.constant_quality is not None:
		modifiers.append(QualitySetter(args.constant_quality))
	if args.fasta:
		modifiers.append(quality_dropper)
	if args.unique_names:
		modifiers.append(UniqueNamer())
	with SequenceReader(args.path) as fr:
		format = fr.format
		outformat = format
		if args.constant_quality is not None:
			outformat = 'fastq'
		if args.fasta:
			outformat = 'fasta'
		if outformat == 'fastq':
			writer = FastqWriter(sys.stdout)
		else:
			writer = FastaWriter(sys.stdout, line_length=args.width)
		try:
			for record in fr:
				for modifier in modifiers:
					record = modifier(record)
					if record is None:
						break
				else:
					# only executed if loop did not terminate via break
					writer.write(record)
		except IOError as e:
			if e.errno != errno.EPIPE:
				raise


if __name__ == '__main__':
	main()
