import numpy as np
import time
import sys
from optparse import OptionParser
import leapUtils
import leapMain
import fastlmm.association
np.set_printoptions(precision=4, linewidth=200)


parser = OptionParser()
parser.add_option('--bfilesim', metavar='bfilesim', default=None, help='Binary plink file')
parser.add_option('--bfile', metavar='bfile', default=None, help='Binary plink file to test')
parser.add_option('--pheno', metavar='pheno', default=None, help='Phenotype file in Plink format')
parser.add_option('--eigen', metavar='eigen', default=None, help='Eigendecompositon file')
parser.add_option('--h2', metavar='h2', type=float, default=None, help='h2 value')
parser.add_option('--extractSim', metavar='extractSim', default=None, help='SNPs subset to use')
parser.add_option('--extract', metavar='extract', default=None, help='SNPs subset to test')
parser.add_option('--out', metavar='out', default=None, help='output file')
parser.add_option('--covar', metavar='covar', default=None, help='Covariates file')
parser.add_option('--missingPhenotype', metavar='missingPhenotype', default='-9', help='identifier for missing values (default: -9)')
(options, args) = parser.parse_args()

def gwas(bedSim, bedTest, pheno, h2, outFile, eigenFile, covar):

	bedSim, pheno = leapUtils._fixupBedAndPheno(bedSim, pheno)
	bedTest, pheno = leapUtils._fixupBedAndPheno(bedTest, pheno)

	#Run GWAS	
	logdelta = np.log(1.0/h2 - 1)
	G0 = (bedSim if eigenFile is None else None)
	print 'Performing LEAP GWAS...'
	results_df = fastlmm.association.single_snp(bedTest, pheno, G0=G0, covar=covar, output_file_name=outFile, log_delta=logdelta, cache_file=eigenFile)
	return results_df
	

if __name__ == '__main__':
	if (options.bfile is None): raise Exception('bfile must be supplied')
	if (options.bfilesim is None): raise Exception('bfilesim must be supplied')
	if (options.pheno is None): raise Exception('phenotype file must be supplied')
	if (options.out is None):   raise Exception('output file name must be supplied')
	if (options.h2 is None): raise Exception('h2 must be supplied')
	
	#Read bfile and pheno file
	bedSim, _ = leapUtils.loadData(options.bfilesim, options.extractSim, options.pheno, options.missingPhenotype, loadSNPs=True)
	bedTest, _ = leapUtils.loadData(options.bfile, options.extract, options.pheno, options.missingPhenotype, loadSNPs=True)

	#Read covariates
	if (options.covar is not None):		
		covar = leapUtils.loadCovars(bed, covar)			
		print 'Read', covarsMat.shape[1], 'covariates from file'
	else: covar = None
	
	leapMain.leapGwas(bedSim, bedTest, options.pheno, options.h2, options.out, eigenFile=options.eigen, covar=covar)

	
