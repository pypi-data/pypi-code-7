import numpy
import unittest
import os

from fieldpy.primitives.axis import axis
from fieldpy.primitives.grid import grid2D, grid3D
from fieldpy.primitives.datafield import datafield2D, datafield3D


class test_datafield2D_toFromH5(unittest.TestCase):
    def setUp(self):
        #create an axis (square grid)
        x = axis(numpy.arange(-0.4, 0.5 + 0.01, 0.01))
        y = axis(numpy.arange(-0.6, 0.7 + 0.02, 0.02))

        #create a 'grid2D'
        g = grid2D(x, y)

        #create a meshgrid with the coordinates
        mg = g.createMeshEdges()

        #create a 2D array with a 2D sinusoidal distribution
        arr = (1.0e3 * numpy.cos(mg[0] ** 2 + mg[1] ** 2) *
               numpy.exp(-1.0 * (mg[0] ** 2 + mg[1] ** 2)))

        self.df = datafield2D(g, arr, "node")

        self.fname = "test.h5"

        if os.path.exists(self.fname):
            os.remove(self.fname)

        self.df.toFile(self.fname)
        self.df2 = datafield2D.fromFile(self.fname)

    def test_axes(self):
        self.assertTrue((self.df.dataGrid.axis_x.coordsEdges ==
                         self.df2.dataGrid.axis_x.coordsEdges).all())
        self.assertTrue((self.df.dataGrid.axis_y.coordsEdges ==
                         self.df2.dataGrid.axis_y.coordsEdges).all())

    def test_data(self):
        self.assertTrue((self.df.dataArray ==
                         self.df2.dataArray).all())

    def tearDown(self):
        if os.path.exists(self.fname):
            os.remove(self.fname)


class test_datafield2D_toFromMAT(unittest.TestCase):
    def setUp(self):
        #create an axis (square grid)
        x = axis(numpy.arange(-0.4, 0.5 + 0.01, 0.01))
        y = axis(numpy.arange(-0.6, 0.7 + 0.02, 0.02))

        #create a 'grid2D'
        g = grid2D(x, y)

        #create a meshgrid with the coordinates
        mg = g.createMeshEdges()

        #create a 2D array with a 2D sinusoidal distribution
        arr = (1.0e3 * numpy.cos(mg[0] ** 2 + mg[1] ** 2) *
               numpy.exp(-1.0 * (mg[0] ** 2 + mg[1] ** 2)))

        self.df = datafield2D(g, arr, "node")

        self.fname = "test.mat"

        if os.path.exists(self.fname):
            os.remove(self.fname)

        self.df.toFile(self.fname)
        self.df2 = datafield2D.fromFile(self.fname)

    def test_axes(self):
        self.assertTrue((self.df.dataGrid.axis_x.coordsEdges ==
                         self.df2.dataGrid.axis_x.coordsEdges).all())
        self.assertTrue((self.df.dataGrid.axis_y.coordsEdges ==
                         self.df2.dataGrid.axis_y.coordsEdges).all())

    def test_data(self):
        self.assertTrue((self.df.dataArray ==
                         self.df2.dataArray).all())

    def tearDown(self):
        if os.path.exists(self.fname):
            os.remove(self.fname)


class test_datafield2D_toFromMHD(unittest.TestCase):
    def setUp(self):
        #create an axis (square grid)
        x = axis(numpy.arange(-0.4, 0.5 + 0.01, 0.01))
        y = axis(numpy.arange(-0.6, 0.7 + 0.02, 0.02))

        #create a 'grid2D'
        g = grid2D(x, y)

        #create a meshgrid with the coordinates
        mg = g.createMeshEdges()

        #create a 2D array with a 2D sinusoidal distribution
        arr = (1.0e3 * numpy.cos(mg[0] ** 2 + mg[1] ** 2) *
               numpy.exp(-1.0 * (mg[0] ** 2 + mg[1] ** 2)))

        self.df = datafield2D(g, arr, "node")

        self.fname = "test.mhd"

        if os.path.exists(self.fname):
            os.remove(self.fname)
            os.remove(self.fname.replace(".mhd", ".raw"))

        self.df.toFile(self.fname)
        self.df2 = datafield2D.fromFile(self.fname)

    def test_axes(self):
            self.assertTrue((self.df.dataGrid.axis_x.coordsEdges ==
                             self.df2.dataGrid.axis_x.coordsEdges).all())

    def test_data(self):
        self.assertTrue((self.df.dataArray ==
                         self.df2.dataArray).all())

    def tearDown(self):
        if os.path.exists(self.fname):
            os.remove(self.fname)
            os.remove(self.fname.replace(".mhd", ".raw"))


class test_datafield3D_toFromH5(unittest.TestCase):
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

        self.fname = "test.h5"

        if os.path.exists(self.fname):
            os.remove(self.fname)

        self.df.toFile(self.fname)
        self.df2 = datafield3D.fromFile(self.fname)

    def test_axes(self):
        self.assertTrue((self.df.dataGrid.axis_x.coordsEdges ==
                         self.df2.dataGrid.axis_x.coordsEdges).all())
        self.assertTrue((self.df.dataGrid.axis_y.coordsEdges ==
                         self.df2.dataGrid.axis_y.coordsEdges).all())
        self.assertTrue((self.df.dataGrid.axis_z.coordsEdges ==
                         self.df2.dataGrid.axis_z.coordsEdges).all())

    def test_data(self):
        self.assertTrue((self.df.dataArray ==
                         self.df2.dataArray).all())

    def tearDown(self):
        if os.path.exists(self.fname):
            os.remove(self.fname)


class test_datafield3D_toFromMAT(unittest.TestCase):
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

        self.fname = "test.mat"

        if os.path.exists(self.fname):
            os.remove(self.fname)

        self.df.toFile(self.fname)
        self.df2 = datafield3D.fromFile(self.fname)

    def test_axes(self):
        self.assertTrue((self.df.dataGrid.axis_x.coordsEdges ==
                         self.df2.dataGrid.axis_x.coordsEdges).all())
        self.assertTrue((self.df.dataGrid.axis_y.coordsEdges ==
                         self.df2.dataGrid.axis_y.coordsEdges).all())
        self.assertTrue((self.df.dataGrid.axis_z.coordsEdges ==
                         self.df2.dataGrid.axis_z.coordsEdges).all())

    def test_data(self):
        self.assertTrue((self.df.dataArray ==
                         self.df2.dataArray).all())

    def tearDown(self):
        if os.path.exists(self.fname):
            os.remove(self.fname)


class test_datafield3D_toFromMHD(unittest.TestCase):
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

        self.fname = "test.mhd"

        if os.path.exists(self.fname):
            os.remove(self.fname)
            os.remove(self.fname.replace(".mhd", ".raw"))

        self.df.toFile(self.fname)
        self.df2 = datafield3D.fromFile(self.fname)

    def test_axes(self):
        self.assertTrue((self.df.dataGrid.axis_x.coordsEdges ==
                         self.df2.dataGrid.axis_x.coordsEdges).all())
        self.assertTrue((self.df.dataGrid.axis_y.coordsEdges ==
                         self.df2.dataGrid.axis_y.coordsEdges).all())
        self.assertTrue((self.df.dataGrid.axis_z.coordsEdges ==
                         self.df2.dataGrid.axis_z.coordsEdges).all())

    def test_data(self):
        self.assertTrue((self.df.dataArray ==
                         self.df2.dataArray).all())

    def tearDown(self):
        if os.path.exists(self.fname):
            os.remove(self.fname)
            os.remove(self.fname.replace(".mhd", ".raw"))