import numpy as np
from optparse import OptionParser
import time
import scipy.linalg.blas as blas
import leapUtils
np.set_printoptions(precision=3, linewidth=200)
import leapMain

parser = OptionParser()
parser.add_option('--bfilesim', metavar='bfilesim', default=None, help='Binary plink file')
parser.add_option('--extractSim', metavar='extractSim', default=None, help='extractSim file')
parser.add_option('--cutoff', metavar='cutoff', type=float, default=0.05, help='Relationship cutoff (default 0.05)')
parser.add_option('--out', metavar='out', default=None, help='output file')

parser.add_option('--pheno', metavar='pheno', default=None, help='Phenotypes file (optional), only used for identifying unphenotyped individuals')
parser.add_option('--missingPhenotype', metavar='missingPhenotype', default='-9', help='identifier for missing values (default: -9)')
(options, args) = parser.parse_args()



def findRelated(bed, outFile, cutoff):

	bed = leapUtils._fixupBed(bed)
	
	keepArr = leapUtils.findRelated(bed, cutoff)
	if (outFile is not None):
		print 'Printing output to', outFile
		f = open(outFile, 'w')
		for i, (fid,iid) in enumerate(bed.iid):
			if (keepArr[i]): f.write(fid + ' ' + iid + ' 0\n')
			else: f.write(fid + ' ' + iid + ' 1\n')
		f.close()
	return keepArr
	
if __name__ == '__main__':
	if (options.bfilesim is None): raise Exception('bfilesim must be supplied')
	if (options.out is None):   raise Exception('output file name must be supplied')
	bed, _ = leapUtils.loadData(options.bfilesim, options.extractSim, options.pheno, options.missingPhenotype, loadSNPs=True, standardize=True)
	leapMain.findRelated(bed, options.out, options.cutoff)
	
