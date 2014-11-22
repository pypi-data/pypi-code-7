import numpy
import unittest
import os

from fieldpy.primitives.axis import axis
from fieldpy.primitives.grid import grid2D
from fieldpy.primitives.datafield import datafield2D
from fieldpy.analysis.gammaAnalysis import gammaCalculator2D

#OPTIONS
cfd = os.path.dirname(os.path.realpath(__file__))
fnameMes2D = os.path.join(cfd, "data", "df2dMes.mhd")
fnameSim2D = os.path.join(cfd, "data", "df2dSimReg.mhd")
fnameGamma2D = os.path.join(cfd, "data", "dfGamma2D_Mes_SimReg.mhd")


class test_gamma2D_basic(unittest.TestCase):
    def setUp(self):
        xRef = axis(numpy.arange(-7.5, 7.5 + 0.5, 0.5))
        xEval = axis(numpy.arange(-10.0, 10.0 + 0.1, 0.1))

        gRef = grid2D(xRef, xRef)
        gEval = grid2D(xEval, xEval)

        mgRef = gRef.createMeshCenters()
        mgEval = gEval.createMeshCenters()

        arrRef = 1000 * (numpy.exp(-1.0 * (mgRef[0] ** 2 +
                                           mgRef[1] ** 2)))

        arrEval = 1000 * (numpy.exp(-1.0 * (mgEval[0] ** 2 +
                                            mgEval[1] ** 2)))

        dfRef = datafield2D(gRef, arrRef, "center")
        dfEvalSame = datafield2D(gEval, arrEval, "center", deepCopy=True)

        arrEval[60:140, 90:110] += 100
        arrEval[90:110, 70:130] += 50
        dfEvalDiff = datafield2D(gEval, arrEval, "center", deepCopy=True)

        self.gCsame = gammaCalculator2D(dfRef, dfEvalSame)
        self.dfGammaSame = self.gCsame.calculateGamma(1.0, 0.1)
        self.gCdiff = gammaCalculator2D(dfRef, dfEvalDiff)
        self.dfGammaDiff = self.gCdiff.calculateGamma(1.0, 0.1)

    def test_percentiles(self):
        self.assertLessEqual(numpy.percentile(self.dfGammaSame.dataArray,
                                              99),
                             1.0e-3)
        self.assertLessEqual(numpy.percentile(self.dfGammaDiff.dataArray,
                                              50),
                             1.0e-3)
        self.assertGreaterEqual(numpy.percentile(self.dfGammaDiff.dataArray,
                                                 99),
                                10.0)


class test_gamma2D_real(unittest.TestCase):
    def setUp(self):

        #load data
        self.dfMes = datafield2D.fromFile(fnameMes2D)
        self.dfSim = datafield2D.fromFile(fnameSim2D)
        self.dfGammaRef = datafield2D.fromFile(fnameGamma2D)

        self.gC = gammaCalculator2D(self.dfMes, self.dfSim)
        self.dfGamma = self.gC.calculateGamma(2.7, 0.25)

    def test_percentiles(self):
        self.assertLessEqual(numpy.percentile(self.dfGamma.dataArray,
                                              90),
                             1.0)

    def test_maxGamma(self):
        self.assertLessEqual(self.dfGamma.dataArray.max(), 1.4)

    def test_dfGamma(self):
        self.assertTrue((self.dfGamma.dataArray ==
                         self.dfGammaRef.dataArray).all())