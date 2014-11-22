import numpy
import os
import unittest

from fieldpy.primitives.axis import axis
from fieldpy.primitives.grid import grid2D, grid3D
from fieldpy.primitives.point import pointCart2D, pointCart3D
from fieldpy.primitives.datafield import datafield2D, datafield3D
from fieldpy.analysis.locExAnalysis import locExExtractor, locExAnalyzer

#OPTIONS
cfd = os.path.dirname(os.path.realpath(__file__))
fnameDfTemp2D = os.path.join(cfd, "data", "dfTemp2D.h5")
fnameDfTemp3D = os.path.join(cfd, "data", "dfTemp3D.h5")


class test_locExAnalysis_case2D(unittest.TestCase):
    def setUp(self):
        # load 2D datafield
        self.df = datafield2D.fromFile(fnameDfTemp2D)

        # create a 'locExExtractor'
        self.lee = locExExtractor(self.df)

        self.locExs, _map = self.lee.extractExtrema(strType="max",
                                                    connectivity=2,
                                                    thresholdLow=13.0)

        self.lea = locExAnalyzer(self.locExs)

        self.leMax = self.lea.findMaximum()
        self.leMin = self.lea.findMinimum()
        diff, self.leClosestValue = self.lea.findClosestValue(26.0)
        dist, self.leNearest = self.lea.findNearest(pointCart2D([0.08, 0.14]))

    def test_noLocExs(self):
        self.assertEqual(6, len(self.locExs))

    def test_leMax_value(self):
        self.assertAlmostEquals(87.64, self.leMax.value, 2)

    def test_leMax_index(self):
        self.assertEquals(82, self.leMax.index.i)
        self.assertEquals(77, self.leMax.index.j)

    def test_leMax_coords(self):
        self.assertAlmostEquals(0.095, self.leMax.coords.x, 3)
        self.assertAlmostEquals(0.150, self.leMax.coords.y, 3)

    def test_leMin_value(self):
        self.assertAlmostEquals(13.47, self.leMin.value, 2)

    def test_leMin_index(self):
        self.assertEquals(58, self.leMin.index.i)
        self.assertEquals(86, self.leMin.index.j)

    def test_leMin_coords(self):
        self.assertAlmostEquals(0.063, self.leMin.coords.x, 3)
        self.assertAlmostEquals(0.161, self.leMin.coords.y, 3)

    def test_leClosestValue_value(self):
        self.assertAlmostEquals(26.52, self.leClosestValue.value, 2)

    def test_leClosestValue_index(self):
        self.assertEquals(56, self.leClosestValue.index.i)
        self.assertEquals(76, self.leClosestValue.index.j)

    def test_leClosestValue_coords(self):
        self.assertAlmostEquals(0.061, self.leClosestValue.coords.x, 3)
        self.assertAlmostEquals(0.149, self.leClosestValue.coords.y, 3)

    def test_leNearest_value(self):
        self.assertAlmostEquals(17.13, self.leNearest.value, 2)

    def test_leNearest_index(self):
        self.assertEquals(70, self.leNearest.index.i)
        self.assertEquals(71, self.leNearest.index.j)

    def test_leNearest_coords(self):
        self.assertAlmostEquals(0.079, self.leNearest.coords.x, 3)
        self.assertAlmostEquals(0.142, self.leNearest.coords.y, 3)

    def test_BestV2D(self):
        self.assertEquals(self.lea.findBestV2D(pointCart2D([0.0948, 0.151]))[1],
                          self.leMax)


class test_locExAnalysis_case3D(unittest.TestCase):
    def setUp(self):
        # load datafield
        self.df = datafield3D.fromFile(fnameDfTemp3D)

        #create a locExExtractor
        self.lee = locExExtractor(self.df)

        self.locExs, _map = self.lee.extractExtrema(strType="max",
                                                    connectivity=2,
                                                    thresholdLow=13.0)

        self.lea = locExAnalyzer(self.locExs)

        self.leMax = self.lea.findMaximum()
        self.leMin = self.lea.findMinimum()
        diff, self.leClosestValue = self.lea.findClosestValue(26.0)
        dist, self.leNearest = self.lea.findNearest(
            pointCart3D([0.108, 0.070, 0.160]))

    def test_noLocExs(self):
        self.assertEqual(73, len(self.locExs))

    def test_leMax_value(self):
        self.assertAlmostEquals(88.22, self.leMax.value, 2)

    def test_leMax_index(self):
        self.assertEquals(132, self.leMax.index.i)
        self.assertEquals(82, self.leMax.index.j)
        self.assertEquals(77, self.leMax.index.k)

    def test_leMax_coords(self):
        self.assertAlmostEquals(0.095, self.leMax.coords.x, 3)
        self.assertAlmostEquals(0.095, self.leMax.coords.y, 3)
        self.assertAlmostEquals(0.150, self.leMax.coords.z, 3)

    def test_leMin_value(self):
        self.assertAlmostEquals(13.04, self.leMin.value, 2)

    def test_leMin_index(self):
        self.assertEquals(132, self.leMin.index.i)
        self.assertEquals(45, self.leMin.index.j)
        self.assertEquals(67, self.leMin.index.k)

    def test_leMin_coords(self):
        self.assertAlmostEquals(0.095, self.leMin.coords.x, 3)
        self.assertAlmostEquals(0.045, self.leMin.coords.y, 3)
        self.assertAlmostEquals(0.136, self.leMin.coords.z, 3)

    def test_leClosestValue_value(self):
        self.assertAlmostEquals(26.15, self.leClosestValue.value, 2)

    def test_leClosestValue_index(self):
        self.assertEquals(139, self.leClosestValue.index.i)
        self.assertEquals(68, self.leClosestValue.index.j)
        self.assertEquals(80, self.leClosestValue.index.k)

    def test_leClosestValue_coords(self):
        self.assertAlmostEquals(0.107, self.leClosestValue.coords.x, 3)
        self.assertAlmostEquals(0.076, self.leClosestValue.coords.y, 3)
        self.assertAlmostEquals(0.153, self.leClosestValue.coords.z, 3)

    def test_leNearest_value(self):
        self.assertAlmostEquals(17.71, self.leNearest.value, 2)

    def test_leNearest_index(self):
        self.assertEquals(140, self.leNearest.index.i)
        self.assertEquals(62, self.leNearest.index.j)
        self.assertEquals(87, self.leNearest.index.k)

    def test_leNearest_coords(self):
        self.assertAlmostEquals(0.1085, self.leNearest.coords.x, 3)
        self.assertAlmostEquals(0.0683, self.leNearest.coords.y, 3)
        self.assertAlmostEquals(0.1627, self.leNearest.coords.z, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)