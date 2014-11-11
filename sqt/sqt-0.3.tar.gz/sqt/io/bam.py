#!/usr/bin/env python3
from collections import namedtuple
from struct import calcsize, unpack, unpack_from
import gzip
from itertools import chain
import sys

Reference = namedtuple('Reference', ['name', 'length'])

class FormatError:
	pass

SEQ_TRANS = bytes.maketrans(bytes(range(16)), b'=ACMGRSVTWYHKDBN')
CIGAR_OPS = 'MIDNSHP=X'
QUAL_TRANS = bytes.maketrans(bytes(range(100)), bytes(range(33, 133)))

class BamAlignment:
	def __init__(self, data, references):
		self.references = references
		align = '<iiIIiiii'
		ref_id, pos, bin_mq_nl, flag_nc, l_seq, next_ref_id, next_pos, tlen = \
			unpack_from(align, data)
		#bin = bin_mq_nl >> 16
		mapq = (bin_mq_nl & 0xFF00) >> 8
		read_name_length = bin_mq_nl & 0xFF
		flags = flag_nc >> 16
		n_cigar_op = flag_nc & 0xFFFF
		n = calcsize(align)
		read_name = data[n: n + read_name_length - 1] # NULL-terminated
		offset = n + read_name_length
		cigar_codes = unpack_from('<{}I'.format(n_cigar_op), data, offset = offset)
		offset += 4 * n_cigar_op
		encoded_seq = data[offset:offset + (l_seq + 1) // 2]
		offset += (l_seq + 1) // 2
		qual = data[offset:offset + l_seq]
		if qual[0] == 255:
			qual = None

		seq = bytes(chain(*[(v>>4, v&0xF) for v in encoded_seq]))
		seq = seq.translate(SEQ_TRANS)
		if l_seq & 1 == 1: # if odd
			seq = seq[:l_seq]

		# parsing is done here, now format data for printing
		# TODO tags
		if qual:
			qual_string = qual.translate(QUAL_TRANS).decode('ascii')
		else:
			qual_string = '*'
		cigar = [ (code >> 4, CIGAR_OPS[code&0xF]) for code in cigar_codes ]
		if not cigar:
			cigar_string = '*'
		else:
			cigar_string = ''.join('{}{}'.format(*op) for op in cigar)

		ref_name = self.references[ref_id].name.decode('ascii') if ref_id >= 0 else '*'
		if next_ref_id == ref_id:
			next_ref_name = '='
		else:
			next_ref_name = self.references[next_ref_id].name.decode('ascii') if next_ref_id >= 0 else '*'
		# note: pos and next_pos can have value -1

		# TODO only for testing
		self.sam = '\t'.join((
			read_name.decode('ascii'),
			str(flags),
			ref_name,
			str(pos + 1),
			str(mapq),
			cigar_string,
			next_ref_name,
			str(next_pos + 1),
			str(tlen),
			seq.decode('ascii'),
			qual_string))


class BamReader:
	MAGIC = b'BAM\1'

	def __init__(self, file):
		"""
		open the file, read the header
		"""
		file = gzip.GzipFile(file, 'rb')
		data = file.read(4)
		if data != self.MAGIC:
			raise FormatError("magic bytes 'BAM\\1' not found, is this a BAM file?")
		# header in SAM text format
		header_length = unpack('<i', file.read(4))[0]
		header = file.read(header_length)
		# BAM header with reference sequence names and lengths
		n = unpack('<i', file.read(4))[0]
		refs = []
		for i in range(n):
			ref_name_length = unpack('<i', file.read(4))[0]
			ref_name = file.read(ref_name_length)[:-1] # NULL-terminated
			ref_length = unpack('<i', file.read(4))[0]
			refs.append(Reference(ref_name, ref_length))
		self.references = refs
		self.file = file

	def __iter__(self):
		while True:
			data = self.file.read(4)
			if len(data) < 4:
				break
			block_size = unpack('<i', data)[0]
			data = self.file.read(block_size)
			yield BamAlignment(data, self.references)

def main():
	for alignment in BamReader(sys.argv[1]):
		print(alignment.sam)


if __name__ == '__main__':
	main()
