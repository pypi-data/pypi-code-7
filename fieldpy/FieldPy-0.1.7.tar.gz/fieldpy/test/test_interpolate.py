import numpy
import unittest

from fieldpy.primitives.axis import axis
from fieldpy.primitives.grid import grid2D, grid3D
from fieldpy.interpolation import interpolate

class test_interpolate_simple2D(unittest.TestCase):
    def setUp(self):

        #create an axis (square grid)
        x_old = axis(numpy.arange(-2.0, 2.0 + 0.1, 0.1))
        x_new = axis(numpy.arange(-2.0, 2.0 + 0.05, 0.05))

        #create a 'grid2D'
        g = grid2D(x_old, x_old)

        #create a meshgrid with the coordinates
        mg = g.createMeshEdges()

        #create a 2D array with a 2D sinusoidal distribution
        self.arr = 1.0e3*numpy.sin(mg[0] ** 2 + mg[1] ** 2)

        self.arrOS = interpolate.interpolate2D(x_old.coordsEdges,
                                               x_old.coordsEdges,
                                               self.arr,
                                               x_new.coordsEdges,
                                               x_new.coordsEdges,
                                               1)
    def test_OS(self):
        self.assertAlmostEquals(self.arr.max(), self.arrOS.max(), 3)
        self.assertAlmostEquals(self.arr.min(), self.arrOS.min(), 3)

class test_interpolate_simple3D(unittest.TestCase):
    def setUp(self):

        #create an axis (square grid)
        x_old = axis(numpy.arange(-2.0, 2.0 + 0.1, 0.1))
        x_new = axis(numpy.arange(-2.0, 2.0 + 0.05, 0.05))

        #create a 'grid3D'
        g = grid3D(x_old, x_old, x_old)

        #create a meshgrid with the coordinates
        mg = g.createMeshEdges()

        #create a 3D array with a 3D sinusoidal distribution
        self.arr = 1.0e3*numpy.sin(mg[0] ** 2 + mg[1] ** 2 + mg[2] ** 2)

        #interpolate to a twice-as-fine grid with an first order interpolation
        self.arrOS = interpolate.interpolate3D(x_old.coordsEdges,
                                               x_old.coordsEdges,
                                               x_old.coordsEdges,
                                               self.arr,
                                               x_new.coordsEdges,
                                               x_new.coordsEdges,
                                               x_new.coordsEdges,
                                               1)

    def test_OS(self):
        self.assertAlmostEquals(self.arr.max(), self.arrOS.max(), 3)
        self.assertAlmostEquals(self.arr.min(), self.arrOS.min(), 3)

if __name__ == "__main__":
    unittest.main(verbosity=2)