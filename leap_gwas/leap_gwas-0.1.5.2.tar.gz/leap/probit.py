import numpy as np
import scipy.stats as stats
import scipy.linalg as la
import time
import sklearn.linear_model
import sys
from optparse import OptionParser
import scipy.optimize as opt
import scipy.linalg.blas as blas
import leapUtils
import leapMain
np.set_printoptions(precision=6, linewidth=200)





parser = OptionParser()
parser.add_option('--bfilesim', metavar='bfilesim', default=None, help='Binary plink file')
parser.add_option('--pheno', metavar='pheno', default=None, help='Phenotype file in Plink format')
parser.add_option('--h2', metavar='h2', type=float, default=None, help='Liability heritability')
parser.add_option('--eigen', metavar='eigen', default=None, help='eigen file')
parser.add_option('--prev', metavar='prev', type=float, default=None, help='Trait prevalence')
parser.add_option('--extractSim', metavar='extractSim', default=None, help='SNPs subset to use')
parser.add_option('--out', metavar='out', default=None, help='output file')

parser.add_option('--covar', metavar='covar', default=None, help='covariates file in FastLMM format')
parser.add_option('--thresholds', metavar='thresholds', default=None, help="liability thresholds file")
parser.add_option('--nofail', metavar='nofail', type=int, default=0, help="Do not raise exception if Probit fitting failed")

parser.add_option('--relCutoff', metavar='relCutoff', type=float, default=0.05, help='Relatedness cutoff')
parser.add_option('--numSkipTopPCs', metavar='numSkipTopPCs', type=int, default=0, help='Number of PCs to skip')
parser.add_option('--numFixedPCs', metavar='numFixedPCs', type=int, default=0, help='Number of PCs to use as fixed effects')
parser.add_option('--hess', metavar='hess', type=int, default=1, help='Whether to compute Hessian analytically (1) or not (0)')
parser.add_option('--bfile', metavar='bfile', default=None, help='Binary plink file with SNPs that can be used as fixed effects')
parser.add_option('--resfile', metavar='resfile', default=None, help='A linear regression results file in FastLMM format, used to choose SNPs that will be used as fixed effects')
parser.add_option('--pthresh', metavar='pthresh', type=float, default=5e-8, help='p-value cutoff below which SNPs will be used as fixed effects')
parser.add_option('--mineig', metavar='mineig', type=float, default=1e-3, help='eigenvectors with singular value below this value will not be used')
parser.add_option('--extract', metavar='extract', default=None, help='subset of SNPs to be considered as fixed effects')
parser.add_option('--related', metavar='related', default=None, help='File with info about related individuals to remove')
parser.add_option('--mindist', metavar='mindist', type=int, default=0, help='Minimum distance between fixed effects SNPs')
parser.add_option('--recenter', metavar='recenter', type=int, default=1, help='Whether to recenter features matrix so that only individuals participating in the model fitting stage will have zero mean for every feature (1 or 0)')
parser.add_option('--maxFixedIters', metavar='maxFixedIters', type=int, default=100, help='Max number of iterations for fitting of fixed effects')
parser.add_option('--epsilon', metavar='epsilon', type=float, default=1e-3, help='Convergence cutoff for fitting of fixed effects')
parser.add_option('--missingPhenotype', metavar='missingPhenotype', default='-9', help='identifier for missing values (default: -9)')
(options, args) = parser.parse_args()




def evalProbitReg(beta, X, cases, controls, thresholds, invRegParam, normPDF, h2):
	XBeta = np.ravel(X.dot(beta)) - thresholds
	phiXBeta = normPDF.pdf(XBeta)
	PhiXBeta = normPDF.cdf(XBeta)
	
	logLik = np.sum(np.log(PhiXBeta[cases])) + np.sum(np.log(1-PhiXBeta[controls]))	
	w = np.zeros(X.shape[0])
	w[cases] = -phiXBeta[cases] / PhiXBeta[cases]
	w[controls] = phiXBeta[controls] / (1-PhiXBeta[controls])
	grad = X.T.dot(w)
	
	#regularize
	logLik -= 0.5*invRegParam * beta.dot(beta)	#regularization	
	grad += invRegParam * beta
	return (-logLik, grad)

	
def probitRegHessian(beta, X, cases, controls, thresholds, invRegParam, normPDF, h2):
	XBeta = np.ravel(X.dot(beta)) - thresholds
	phiXBeta = normPDF.pdf(XBeta)
	PhiXBeta = normPDF.cdf(XBeta)
	
	XbetaScaled = XBeta #/(1-h2)
	
	R = np.zeros(X.shape[0])
	R[cases] 	= (XbetaScaled[cases]*PhiXBeta[cases] 			+ phiXBeta[cases]) 	 / PhiXBeta[cases]**2
	R[controls] = (-XbetaScaled[controls]*(1-PhiXBeta[controls]) 	+ phiXBeta[controls]) / (1 - PhiXBeta[controls])**2

	R *= phiXBeta	
	H = (X.T * R).dot(X)	
	H += invRegParam
	return H
	

def probitRegression(X, y, thresholds, numSNPs, numFixedFeatures, h2, useHess, maxFixedIters, epsilon, nofail):

	regParam = h2 /  float(numSNPs)	
	Linreg = sklearn.linear_model.Ridge(alpha=1.0/(2*regParam), fit_intercept=False, normalize=False, solver='lsqr')		
	Linreg.fit(X, y)
	initBeta = Linreg.coef_
	np.random.seed(1234)
	
	normPDF = stats.norm(0, np.sqrt(1-h2))
	invRegParam = 1.0/regParam		
	controls = (y==0)
	cases = (y==1)
	funcToSolve = evalProbitReg
	hess =(probitRegHessian if useHess else None)
	jac= True
	method = 'Newton-CG'
	args = (X, cases, controls, thresholds, invRegParam, normPDF, h2)
	print 'Beginning Probit regression...'
	t0 = time.time()
	optObj = opt.minimize(funcToSolve, x0=initBeta, args=args, jac=jac, method=method, hess=hess)
	print 'Done in', '%0.2f'%(time.time()-t0), 'seconds'	
	if (not optObj.success):
		print 'Optimization status:', optObj.status
		print optObj.message
		if (nofail == 0): raise Exception('Probit regression failed with message: ' + optObj.message)
	beta = optObj.x
			
	#Fit fixed effects
	if (numFixedFeatures > 0):
		thresholdsEM = np.zeros(X.shape[0]) + thresholds
		
		for i in xrange(maxFixedIters):
			print 'Beginning fixed effects iteration', i+1
			t0 = time.time()
			prevBeta = beta.copy()
			
			#Learn fixed effects			
			thresholdsTemp = thresholdsEM - X[:, numFixedFeatures:].dot(beta[numFixedFeatures:])						
			args = (X[:, :numFixedFeatures], cases, controls, thresholdsTemp, 0, normPDF, h2)
				
			optObj = opt.minimize(funcToSolve, x0=beta[:numFixedFeatures], args=args, jac=True, method=method, hess=hess)
			if (not optObj.success): print optObj.message; #raise Exception('Learning failed with message: ' + optObj.message)
			beta[:numFixedFeatures] = optObj.x
			
			#Learn random effects
			thresholdsTemp = thresholdsEM - X[:, :numFixedFeatures].dot(beta[:numFixedFeatures])			
			args = (X[:, numFixedFeatures:], cases, controls, thresholdsTemp, invRegParam, normPDF, h2)
			optObj = opt.minimize(funcToSolve, x0=beta[numFixedFeatures:], args=args, jac=True, method=method, hess=hess)
			if (not optObj.success): print optObj.message; #raise Exception('Learning failed with message: ' + optObj.message)				
			beta[numFixedFeatures:] = optObj.x
			
			diff = np.sqrt(np.mean(beta[:numFixedFeatures]**2 - prevBeta[:numFixedFeatures]**2))
			print 'Done in', '%0.2f'%(time.time()-t0), 'seconds'
			print 'Diff:', '%0.4e'%diff
			if (diff < epsilon): break
	return beta
	


def probit(bed, pheno, h2, prev, eigen, outFile, keepArr, covar, thresholds, nofail,
				numSkipTopPCs, mineig, hess, recenter, maxFixedIters, epsilon):
				
	bed, pheno = leapUtils._fixupBedAndPheno(bed, pheno)
				
	#Extract phenotype
	if isinstance(pheno, dict):	phe = pheno['vals']
	else: phe = pheno		
	if (len(phe.shape)==2):
		if (phe.shape[1]==1): phe=phe[:,0]
		else: raise Exception('More than one phenotype found')		
	if (keepArr is None): keepArr = np.ones(phe.shape[0], dtype=np.bool)				
				
	S = eigen['arr_1'] * bed.sid.shape[0]
	U = eigen['arr_0']
	S = np.sqrt(S)
	goodS = (S>mineig)
	if (numSkipTopPCs > 0): goodS[-numSkipTopPCs:] = False
	if (np.sum(~goodS) > 0): print 'Removing', np.sum(~goodS), 'PCs with low variance'	
	G = U[:, goodS]*S[goodS]
	
	#Set binary vector
	pheUnique = np.unique(phe)
	if (pheUnique.shape[0] != 2): raise Exception('phenotype file has more than two values')
	pheMean = phe.mean()
	cases = (phe>pheMean)
	phe[~cases] = 0
	phe[cases] = 1

	#run probit regression
	t = stats.norm(0,1).isf(prev)
	if (thresholds is not None): t = thresholds

	#Recenter G	to only consider the unrelated individuals
	if recenter: G -= np.mean(G[keepArr, :], axis=0)
	else: G -= np.mean(G, axis=0)
	
	numFixedFeatures = 0
	if (covar is not None):
		covar *= np.mean(np.std(G, axis=0))
		G = np.concatenate((covar, G), axis=1)
		numFixedFeatures += covar.shape[1]

	#Run Probit regression
	probitThresh = (t if thresholds is None else t[keepArr])
	beta = probitRegression(G[keepArr, :], phe[keepArr], probitThresh, bed.sid.shape[0], numFixedFeatures, h2, hess, maxFixedIters, epsilon, nofail)

	#Predict liabilities for all individuals
	meanLiab = G.dot(beta)		
	liab = meanLiab.copy()
	indsToFlip = ((liab <= t) & (phe>0.5)) | ((liab > t) & (phe<0.5))
	liab[indsToFlip] = stats.norm(0,1).isf(prev)
	
	if (outFile is not None):
		#save liabilities
		f = open(outFile+'.liabs', 'w')
		for ind_i,[fid,iid] in enumerate(bed.iid): f.write(' '.join([fid, iid, '%0.3f'%liab[ind_i]]) + '\n')		
		f.close()

		#save liabilities after regressing out the fixed effects
		if (numFixedFeatures > 0):
			liab_nofixed = liab - G[:, :numFixedFeatures].dot(beta[:numFixedFeatures])
			f = open(outFile+'.liab_nofixed', 'w')
			for ind_i,[fid,iid] in enumerate(bed.iid): f.write(' '.join([fid, iid, '%0.3f'%liab_nofixed[ind_i]]) + '\n')		
			f.close()
			
			liab_nofixed2 = meanLiab - G[:, :numFixedFeatures].dot(beta[:numFixedFeatures])
			indsToFlip = ((liab_nofixed2 <= t) & (phe>0.5)) | ((liab_nofixed2 > t) & (phe<0.5))
			liab_nofixed2[indsToFlip] = stats.norm(0,1).isf(prev)
			f = open(outFile+'.liab_nofixed2', 'w')
			for ind_i,[fid,iid] in enumerate(bed.iid): f.write(' '.join([fid, iid, '%0.3f'%liab_nofixed2[ind_i]]) + '\n')		
			f.close()	
			
	#Return phenotype struct with liabilities
	liabsStruct = {
		'header':[None],
		'vals':liab,
		'iid':bed.iid
	}
	return liabsStruct

		
		
if __name__ == '__main__':		
	if (options.extract is not None and options.bfile is None): raise Exception('--extract cannot be used without --bfile')
	if (options.bfile is not None and options.resfile is None): raise Exception('--bfile cannot be used without --resfile')
	if (options.bfilesim is None): raise Exception('bfilesim must be supplied')
	if (options.pheno is None): raise Exception('phenotype file must be supplied')
	if (options.out is None):   raise Exception('output file name must be supplied')
	if (options.prev is None): raise Exception('prevlence must be supplied')
	if (options.h2 is None): raise Exception('heritability must be supplied')
	
	#Read bfilesim and pheno file for heritability computation	
	bed, phe = leapUtils.loadData(options.bfilesim, options.extractSim, options.pheno, options.missingPhenotype, loadSNPs=(options.eigen is None), standardize=True)
	
	#Read/create eigendecomposition
	if (options.eigen is not None): eigen = np.load(options.eigen)
	else:
		import eigenDecompose
		eigen = eigenDecompose.eigenDecompose(bed)	

	#Compute relatedness
	if (options.relCutoff <= 0): keepArr = np.ones(bed.iid.shape[0], dtype=bool)
	else:		
		if (options.related is None):
			bed2 = bed
			if (options.extractSim is not None or options.eigen is not None): bed2, _ = leapUtils.loadData(options.bfilesim, None, options.pheno, options.missingPhenotype, loadSNPs=True)			
			keepArr = leapUtils.findRelated(bed2, options.relCutoff)
		else:
			keepArr = leapUtils.loadRelatedFile(bed, options.related)	
	
	
	#Add significant SNPs as fixed effects	
	covar = None
	if (options.resfile is not None):	
		bed_fixed, _ = leapUtils.loadData(options.bfile, options.extract, options.pheno, options.missingPhenotype, loadSNPs=True)
		covar = leapUtils.getSNPCovarsMatrix(bed_fixed, options.resfile, options.pthresh, options.mindist)		
		print 'using', covar.shape[1], 'SNPs as covariates'		
	#Read covar file
	if (options.covar is not None):		
		covarsMat = leapUtils.loadCovars(bed, covar)			
		print 'Read', covarsMat.shape[1], 'covariates from file'
		if (covar is None): covar = covarsMat
		else: covar = np.concatenate((covar, covarsMat), axis=1)
		
	if (options.thresholds is not None): thresholds = np.loadtxt(options.thresholds, usecols=[0])
	else: thresholds = None
	
	leapMain.probit(bed, phe, options.h2, options.prev, eigen, options.out, keepArr, covar, thresholds, options.nofail==1, 
				options.numSkipTopPCs, options.mineig, options.hess==1, options.recenter==1, options.maxFixedIters, options.epsilon)
		
