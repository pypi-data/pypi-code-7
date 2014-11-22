import numpy
import unittest

from fieldpy.primitives.axis import axis
from fieldpy.primitives.grid import grid3D
from fieldpy.primitives.datafield import datafield3D


class test_datafield3D_basic(unittest.TestCase):
    def setUp(self):
        #create an axis (square grid)
        x = axis(numpy.arange(-0.4, 0.5 + 0.01, 0.01))
        y = axis(numpy.arange(-0.6, 0.7 + 0.02, 0.02))
        z = axis(numpy.arange(-0.8, 0.9 + 0.03, 0.04))

        #create a 'grid3D'
        g = grid3D(x, y, z)

        #create a meshgrid with the coordinates
        mg = g.createMeshEdges()

        #create a 3D array with a 3D sinusoidal distribution
        arr = (1.0e3 * numpy.cos(mg[0] ** 2 + mg[1] ** 2 + mg[2] ** 2) *
               numpy.exp(-1.0 * (mg[0] ** 2 + mg[1] ** 2 + mg[2] ** 2)))

        self.df = datafield3D(g, arr, "node")

    def test_findMaxCoords(self):
        coordsMax = self.df.findMaximumCoords()
        self.assertAlmostEquals(0.0, coordsMax.x, 3)
        self.assertAlmostEquals(0.0, coordsMax.y, 3)
        self.assertAlmostEquals(0.0, coordsMax.z, 3)

    def test_findMaxIdx(self):
        idxMax = self.df.findMaximumIdx()
        self.assertEquals(40, idxMax.i)
        self.assertEquals(30, idxMax.j)
        self.assertEquals(20, idxMax.k)

    def test_shift(self):
        df2 = datafield3D(self.df.dataGrid,
                          self.df.dataArray,
                          self.df.mode,
                          True)
        df2.shiftDatafield([-10.0, -15.0, -20.0])
        coordsMax = df2.findMaximumCoords()
        self.assertAlmostEquals(-10.0, coordsMax.x, 3)
        self.assertAlmostEquals(-15.0, coordsMax.y, 3)
        self.assertAlmostEquals(-20.0, coordsMax.z, 3)

    def test_shiftMaxToOrigin(self):
        df2 = datafield3D(self.df.dataGrid,
                          self.df.dataArray,
                          self.df.mode,
                          True)
        df2.shiftDatafield([-10.0, -15.0, -20.0])
        df2.shiftToOrigin()
        coordsMax = df2.findMaximumCoords()
        idxMax = self.df.findMaximumIdx()
        self.assertAlmostEquals(0.0, coordsMax.x, 3)
        self.assertAlmostEquals(0.0, coordsMax.y, 3)
        self.assertEquals(40, idxMax.i)
        self.assertEquals(30, idxMax.j)

    def test_shiftToOrigin(self):
        df2 = datafield3D(self.df.dataGrid,
                          self.df.dataArray,
                          self.df.mode,
                          True)
        df2.shiftDatafield([-20.0, -10.0, -5.0])
        df2.shiftToOrigin([-10.0, -5.0, -2.5])
        coordsMax = df2.findMaximumCoords()
        idxMax = self.df.findMaximumIdx()
        self.assertAlmostEquals(-10.0, coordsMax.x, 3)
        self.assertAlmostEquals(-5.0, coordsMax.y, 3)
        self.assertAlmostEquals(-2.5, coordsMax.z, 3)

    def test_scaleData(self):
        df2 = datafield3D(self.df.dataGrid,
                          self.df.dataArray,
                          self.df.mode,
                          True)
        df2.scaleData(0.5)
        self.assertAlmostEquals(500.0, df2.dataArray.max(), 0)

    def test_normalizeData(self):
        df2 = datafield3D(self.df.dataGrid,
                          self.df.dataArray,
                          self.df.mode,
                          True)
        df2.normalizeData(2.0)
        self.assertAlmostEquals(2.0, df2.dataArray.max(), 0)


class test_datafield3D_subset(unittest.TestCase):
    def setUp(self):
        #create an axis (square grid)
        x = axis(numpy.arange(-0.4, 0.5 + 0.01, 0.01))
        y = axis(numpy.arange(-0.6, 0.7 + 0.02, 0.02))
        z = axis(numpy.arange(-0.8, 0.9 + 0.03, 0.04))

        #create a 'grid3D'
        g = grid3D(x, y, z)

        #create a meshgrid with the coordinates
        mg = g.createMeshEdges()

        #create a 3D array with a 3D sinusoidal distribution
        arr = (1.0e3 * numpy.cos(mg[0] ** 2 + mg[1] ** 2 + mg[2] ** 2) *
               numpy.exp(-1.0 * (mg[0] ** 2 + mg[1] ** 2 + mg[2] ** 2)))

        self.df = datafield3D(g, arr, "node")
        self.df2 = self.df.createSubset([-0.25, -0.3, -0.35],
                                        [0.25, 0.3, 0.35])
        self.df3 = self.df.createSubset([-0.45, -0.233, -0.05],
                                        [0.11, 100.0, 0.0])

    def test_df2_subset_size(self):
        self.assertEquals(50, self.df2.dataGrid.NOC_X)
        self.assertEquals(30, self.df2.dataGrid.NOC_Y)
        self.assertEquals(18, self.df2.dataGrid.NOC_Z)
        self.assertEquals(51, self.df2.dataGrid.NOE_X)
        self.assertEquals(31, self.df2.dataGrid.NOE_Y)
        self.assertEquals(19, self.df2.dataGrid.NOE_Z)

    def test_df2_subset_coords(self):
        self.assertAlmostEquals(-0.25,
                                self.df2.dataGrid.axis_x.coordsEdges[0],
                                2)
        self.assertAlmostEquals(-0.30,
                                self.df2.dataGrid.axis_y.coordsEdges[0],
                                2)
        self.assertAlmostEquals(-0.36,
                                self.df2.dataGrid.axis_z.coordsEdges[0],
                                2)
        self.assertAlmostEquals(0.25,
                                self.df2.dataGrid.axis_x.coordsEdges[-1],
                                2)
        self.assertAlmostEquals(0.30,
                                self.df2.dataGrid.axis_y.coordsEdges[-1],
                                2)
        self.assertAlmostEquals(0.36,
                                self.df2.dataGrid.axis_z.coordsEdges[-1],
                                2)

    def test_df3_subset_size(self):
        self.assertEquals(51, self.df3.dataGrid.NOC_X)
        self.assertEquals(47, self.df3.dataGrid.NOC_Y)
        self.assertEquals(1, self.df3.dataGrid.NOC_Z)
        self.assertEquals(52, self.df3.dataGrid.NOE_X)
        self.assertEquals(48, self.df3.dataGrid.NOE_Y)
        self.assertEquals(2, self.df3.dataGrid.NOE_Z)

    def test_df3_subset_coords(self):
        self.assertAlmostEquals(-0.40,
                                self.df3.dataGrid.axis_x.coordsEdges[0],
                                2)
        self.assertAlmostEquals(-0.24,
                                self.df3.dataGrid.axis_y.coordsEdges[0],
                                2)
        self.assertAlmostEquals(-0.04,
                                numpy.round(
                                    self.df3.dataGrid.axis_z.coordsEdges[0], 2),
                                2)
        self.assertAlmostEquals(0.11,
                                self.df3.dataGrid.axis_x.coordsEdges[-1],
                                2)
        self.assertAlmostEquals(0.70,
                                numpy.round(
                                    self.df3.dataGrid.axis_y.coordsEdges[-1],
                                    2),
                                2)
        self.assertAlmostEquals(0.0,
                                numpy.round(
                                    self.df3.dataGrid.axis_z.coordsEdges[-1],
                                    2),
                                2)


class test_datafield3D_chMode(unittest.TestCase):
    def setUp(self):
        #create an axis (square grid)
        x = axis(numpy.arange(-0.4, 0.5 + 0.01, 0.01))
        y = axis(numpy.arange(-0.6, 0.7 + 0.02, 0.02))
        z = axis(numpy.arange(-0.8, 0.9 + 0.03, 0.04))

        #create a 'grid3D'
        g = grid3D(x, y, z)

        #create a meshgrid with the coordinates
        mg = g.createMeshEdges()

        #create a 3D array with a 3D sinusoidal distribution
        arr = (1.0e3 * numpy.cos(mg[0] ** 2 + mg[1] ** 2 + mg[2] ** 2) *
               numpy.exp(-1.0 * (mg[0] ** 2 + mg[1] ** 2 + mg[2] ** 2)))

        self.df = datafield3D(g, arr, "node")
        self.df2 = self.df.convertNode2Center()

    def test_mode(self):
        self.assertEquals("center", self.df2.mode)

    def test_grid(self):
        self.assertEquals(self.df.dataGrid.NOC_X + 1,
                          self.df2.dataGrid.NOC_X)
        self.assertEquals(self.df.dataGrid.NOC_Y + 1,
                          self.df2.dataGrid.NOC_Y)
        self.assertEquals(self.df.dataGrid.NOC_Z + 1,
                          self.df2.dataGrid.NOC_Z)
        self.assertEquals(self.df.dataGrid.NOE_X + 1,
                          self.df2.dataGrid.NOE_X)
        self.assertEquals(self.df.dataGrid.NOE_Y + 1,
                          self.df2.dataGrid.NOE_Y)
        self.assertEquals(self.df.dataGrid.NOE_Z + 1,
                          self.df2.dataGrid.NOE_Z)

    def test_array(self):
        self.assertTupleEqual(self.df.dataArray.shape,
                              self.df2.dataArray.shape)
        self.assertTrue((self.df.dataArray == self.df2.dataArray).all())