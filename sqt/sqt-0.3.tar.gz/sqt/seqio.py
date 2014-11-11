import warnings
warnings.warn("This module is deprecated. Please use sqt.io.fasta instead.",
     DeprecationWarning, 2)

from .io.fasta import FastaReader, FastqReader #@UnusedImport
