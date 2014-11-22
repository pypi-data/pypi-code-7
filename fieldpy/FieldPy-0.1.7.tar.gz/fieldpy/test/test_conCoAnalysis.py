import numpy
import unittest

from fieldpy.primitives.axis import axis
from fieldpy.primitives.grid import grid2D, grid3D
from fieldpy.primitives.point import pointCart2D, pointCart3D
from fieldpy.primitives.datafield import datafield2D, datafield3D
from fieldpy.analysis.conCoAnalysis import conCoExtractor, conCoAnalyzer


class test_conCoAnalysis_simple2D(unittest.TestCase):
    def setUp(self):

        # create an axis (square grid)
        x = axis(numpy.arange(-2.0, 2.0 + 0.1, 0.1))

        # create a 'grid2D'
        g = grid2D(x, x)

        # create a meshgrid with the coordinates
        mg = g.createMeshCenters()

        # create a 2D datafield with a 2D sinusoidal distribution
        self.df = datafield2D(g,
                              numpy.sin(mg[0] ** 2 + mg[1] ** 2),
                              "center")

        # create a new 'conCoExtractor'
        self.cce = conCoExtractor(self.df)

        # extract and store the connected-components
        self.conCos = self.cce.extractConCos(thresholdLow=1e-6,
                                             thresholdHigh=1.0)

        # create a new 'conCoAnalyzer'
        self.cca = conCoAnalyzer(self.conCos)

        # get the center component
        self.ccCenter = self.cca.findMaximum()

        #get a corner component
        dist, self.ccCorner = self.cca.findNearest(pointCart2D([1.8, 1.8]))

    def test_noConCos(self):
        self.assertEqual(5, len(self.conCos))

    def test_ccCenter_AV(self):
        self.assertAlmostEquals(9.88, self.ccCenter.AV, 2)

    def test_ccCenter_bbSize(self):
        self.assertAlmostEquals(3.6, self.ccCenter.bbSize.x, 1)
        self.assertAlmostEquals(3.6, self.ccCenter.bbSize.y, 1)

    def test_ccCenter_centerCoords(self):
        self.assertAlmostEquals(0.0, self.ccCenter.centerCoords.x, 0)
        self.assertAlmostEquals(0.0, self.ccCenter.centerCoords.y, 0)

    def test_ccCenter_bbIdxs(self):
        self.assertEquals(2, self.ccCenter.bbIdxsP0.i)
        self.assertEquals(2, self.ccCenter.bbIdxsP0.j)
        self.assertEquals(38, self.ccCenter.bbIdxsP1.i)
        self.assertEquals(38, self.ccCenter.bbIdxsP1.j)

    def test_ccCenter_bbCoords(self):
        self.assertAlmostEquals(-1.8, self.ccCenter.bbCoordsP0.x, 1)
        self.assertAlmostEquals(-1.8, self.ccCenter.bbCoordsP0.y, 1)
        self.assertAlmostEquals(1.8, self.ccCenter.bbCoordsP1.x, 1)
        self.assertAlmostEquals(1.8, self.ccCenter.bbCoordsP1.y, 1)

    def test_ccCenter_valMinMax(self):
        self.assertAlmostEquals(0.99, self.ccCenter.valMax, 1)
        self.assertAlmostEquals(0.05, self.ccCenter.valMin, 1)

    def test_ccCorner_AV(self):
        self.assertAlmostEquals(0.1, self.ccCorner.AV, 1)

    def test_ccCorner_bbSize(self):
        self.assertAlmostEquals(0.4, self.ccCorner.bbSize.x, 1)
        self.assertAlmostEquals(0.4, self.ccCorner.bbSize.y, 1)

    def test_ccCorner_centerCoords(self):
        self.assertAlmostEquals(1.8, self.ccCorner.centerCoords.x, 1)
        self.assertAlmostEquals(1.8, self.ccCorner.centerCoords.y, 1)

    def test_ccCorner_bbIdxs(self):
        self.assertEquals(36, self.ccCorner.bbIdxsP0.i)
        self.assertEquals(36, self.ccCorner.bbIdxsP0.j)
        self.assertEquals(40, self.ccCorner.bbIdxsP1.i)
        self.assertEquals(40, self.ccCorner.bbIdxsP1.j)

    def test_ccCorner_bbCoords(self):
        self.assertAlmostEquals(1.6, self.ccCorner.bbCoordsP0.x, 1)
        self.assertAlmostEquals(1.6, self.ccCorner.bbCoordsP0.y, 1)
        self.assertAlmostEquals(2.0, self.ccCorner.bbCoordsP1.x, 1)
        self.assertAlmostEquals(2.0, self.ccCorner.bbCoordsP1.y, 1)

    def test_ccCorner_valMinMax(self):
        self.assertAlmostEquals(0.97, self.ccCorner.valMax, 1)
        self.assertAlmostEquals(0.20, self.ccCorner.valMin, 1)

class test_conCoAnalysis_simple3D(unittest.TestCase):
    def setUp(self):

        #create an axis (square grid)
        x = axis(numpy.arange(-2.0, 2.0 + 0.1, 0.1))

        #create a 'grid3D'
        g = grid3D(x, x, x)

        #create a meshgrid with the coordinates
        mg = g.createMeshCenters()

        #create a 3D datafield with a 3D sinusoidal distribution
        self.df = datafield3D(g,
                              numpy.sin(mg[0] ** 2 + mg[1] ** 2 + mg[2] ** 2),
                              "center")

        #create a new 'conCoExtractor'
        self.cce = conCoExtractor(self.df)

        #extract and store the connected-components
        self.conCos = self.cce.extractConCos(thresholdLow=1e-6,
                                             thresholdHigh=1.0)

        #create a new 'conCoAnalyzer'
        self.cca = conCoAnalyzer(self.conCos)

        #get the center component
        self.ccCenter = self.cca.findMaximum()

        #get a corner component
        dist, self.ccCorner = self.cca.findNearest(pointCart3D([1.8, 1.8, 1.8]))

    def test_noConCos(self):
        self.assertEqual(2, len(self.conCos))

    def test_ccCenter_AV(self):
        self.assertAlmostEquals(23.24, self.ccCenter.AV, 2)

    def test_ccCenter_bbSize(self):
        self.assertAlmostEquals(3.6, self.ccCenter.bbSize.x, 1)
        self.assertAlmostEquals(3.6, self.ccCenter.bbSize.y, 1)
        self.assertAlmostEquals(3.6, self.ccCenter.bbSize.z, 1)

    def test_ccCenter_centerCoords(self):
        self.assertAlmostEquals(0.0, self.ccCenter.centerCoords.x, 0)
        self.assertAlmostEquals(0.0, self.ccCenter.centerCoords.y, 0)
        self.assertAlmostEquals(0.0, self.ccCenter.centerCoords.z, 0)

    def test_ccCenter_bbIdxs(self):
        self.assertEquals(2, self.ccCenter.bbIdxsP0.i)
        self.assertEquals(2, self.ccCenter.bbIdxsP0.j)
        self.assertEquals(2, self.ccCenter.bbIdxsP0.k)
        self.assertEquals(38, self.ccCenter.bbIdxsP1.i)
        self.assertEquals(38, self.ccCenter.bbIdxsP1.j)
        self.assertEquals(38, self.ccCenter.bbIdxsP1.k)

    def test_ccCenter_bbCoords(self):
        self.assertAlmostEquals(-1.8, self.ccCenter.bbCoordsP0.x, 1)
        self.assertAlmostEquals(-1.8, self.ccCenter.bbCoordsP0.y, 1)
        self.assertAlmostEquals(-1.8, self.ccCenter.bbCoordsP0.z, 1)
        self.assertAlmostEquals(1.8, self.ccCenter.bbCoordsP1.x, 1)
        self.assertAlmostEquals(1.8, self.ccCenter.bbCoordsP1.y, 1)
        self.assertAlmostEquals(1.8, self.ccCenter.bbCoordsP1.z, 1)

    def test_ccCenter_valMinMax(self):
        self.assertAlmostEquals(0.99, self.ccCenter.valMax, 1)
        self.assertAlmostEquals(0.05, self.ccCenter.valMin, 1)

    def test_ccCorner_AV(self):
        self.assertAlmostEquals(8.7, self.ccCorner.AV, 1)

    def test_ccCorner_bbSize(self):
        self.assertAlmostEquals(4.0, self.ccCorner.bbSize.x, 1)
        self.assertAlmostEquals(4.0, self.ccCorner.bbSize.y, 1)
        self.assertAlmostEquals(4.0, self.ccCorner.bbSize.z, 1)

    def test_ccCorner_centerCoords(self):
        self.assertAlmostEquals(0.0, self.ccCorner.centerCoords.x, 1)
        self.assertAlmostEquals(0.0, self.ccCorner.centerCoords.y, 1)
        self.assertAlmostEquals(0.0, self.ccCorner.centerCoords.z, 1)

    def test_ccCorner_bbIdxs(self):
        self.assertEquals(0, self.ccCorner.bbIdxsP0.i)
        self.assertEquals(0, self.ccCorner.bbIdxsP0.j)
        self.assertEquals(0, self.ccCorner.bbIdxsP0.k)
        self.assertEquals(40, self.ccCorner.bbIdxsP1.i)
        self.assertEquals(40, self.ccCorner.bbIdxsP1.j)
        self.assertEquals(40, self.ccCorner.bbIdxsP1.k)

    def test_ccCorner_bbCoords(self):
        self.assertAlmostEquals(-2.0, self.ccCorner.bbCoordsP0.x, 1)
        self.assertAlmostEquals(-2.0, self.ccCorner.bbCoordsP0.y, 1)
        self.assertAlmostEquals(-2.0, self.ccCorner.bbCoordsP0.z, 1)
        self.assertAlmostEquals(2.0, self.ccCorner.bbCoordsP1.x, 1)
        self.assertAlmostEquals(2.0, self.ccCorner.bbCoordsP1.y, 1)
        self.assertAlmostEquals(2.0, self.ccCorner.bbCoordsP1.z, 1)

    def test_ccCorner_valMinMax(self):
        self.assertAlmostEquals(0.97, self.ccCorner.valMax, 1)
        self.assertAlmostEquals(0.0243, self.ccCorner.valMin, 3)

if __name__ == "__main__":
    unittest.main(verbosity=2)