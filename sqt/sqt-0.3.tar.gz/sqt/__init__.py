__version__ = '0.3'

from .args import HelpfulArgumentParser, HelpfulOptionParser
from .io.fasta import (
	SequenceReader, FastaReader, FastqReader, FastaWriter, FastqWriter,
	IndexedFasta, guess_quality_base )
from .io.gtf import GtfReader
from .cigar import Cigar
