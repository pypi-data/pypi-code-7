import numpy
import unittest

from fieldpy.primitives.axis import axis
from fieldpy.primitives.grid import grid2D, grid3D
from fieldpy.primitives.point import pointCart2D, pointCart3D


class test_grid2D_basic(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        self.g = grid2D(x, y)

    def test_noEdges(self):
        self.assertEqual(11, self.g.NOE_X)
        self.assertEqual(5, self.g.NOE_Y)

    def test_noCells(self):
        self.assertEqual(10, self.g.NOC_X)
        self.assertEqual(4, self.g.NOC_Y)

    def test_findCoordEdge(self):
        p = pointCart2D([0.0, 0.0])
        idx = self.g.findCoordsEdgeIdx(p)
        self.assertEqual(5, idx.i)
        self.assertEqual(2, idx.j)

    def test_findCoordCenter(self):
        p = pointCart2D([0.0, 0.0])
        idx = self.g.findCoordsCenterIdx(p)
        self.assertEqual(4, idx.i)
        self.assertEqual(1, idx.j)

    def test_edgeBounds(self):
        pA = pointCart2D([0.0, 0.0])
        pB = pointCart2D([10.0, 0.0])
        self.assertEqual(True, self.g.isCoordsInEdgeBounds(pA))
        self.assertEqual(False, self.g.isCoordsInEdgeBounds(pB))

    def test_centerBounds(self):
        pA = pointCart2D([0.0, 0.0])
        pB = pointCart2D([10.0, 0.0])
        self.assertEqual(True, self.g.isCoordsInCenterBounds(pA))
        self.assertEqual(False, self.g.isCoordsInCenterBounds(pB))

    def test_edgeCoords(self):
        p = self.g.getCoordsEdge([1, 2])
        self.assertEqual(-4.0, p.x)
        self.assertEqual(0.0, p.y)

    def test_centerCoords(self):
        p = self.g.getCoordsCenter([1, 2])
        self.assertEqual(-3.5, p.x)
        self.assertEqual(1.0, p.y)

    def test_BoundingBox(self):
        coordsStart, coordsStop = self.g.getCoordsBounds()
        self.assertAlmostEquals(-5.0, coordsStart.x, 1)
        self.assertAlmostEquals(-4.0, coordsStart.y, 1)
        self.assertAlmostEquals(5.0, coordsStop.x, 1)
        self.assertAlmostEquals(4.0, coordsStop.y, 1)


class test_grid2D_shift(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        self.g = grid2D(x, y)
        self.g.shiftGrid([5, 4])

    def test_coords(self):
        self.assertEqual(0.0, self.g.axis_x.coordsEdges[0])
        self.assertEqual(0.0, self.g.axis_y.coordsEdges[0])

    def test_noEdges(self):
        self.assertEqual(11, self.g.NOE_X)
        self.assertEqual(5, self.g.NOE_Y)

    def test_noCells(self):
        self.assertEqual(10, self.g.NOC_X)
        self.assertEqual(4, self.g.NOC_Y)

    def test_findCoordEdge(self):
        p = pointCart2D([10.0, 8.0])
        idx = self.g.findCoordsEdgeIdx(p)
        self.assertEqual(10, idx.i)
        self.assertEqual(4, idx.j)

    def test_findCoordCenter(self):
        p = pointCart2D([8.0, 4.5])
        idx = self.g.findCoordsCenterIdx(p)
        self.assertEqual(7, idx.i)
        self.assertEqual(2, idx.j)


class test_grid2D_subset(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        self.g = grid2D(x, y)
        self.g = self.g.createSubset([0, 0], [5, 4])

    def test_coords(self):
        self.assertEqual(0.0, self.g.axis_x.coordsEdges[0])
        self.assertEqual(0.0, self.g.axis_y.coordsEdges[0])

    def test_noEdges(self):
        self.assertEqual(6, self.g.NOE_X)
        self.assertEqual(3, self.g.NOE_Y)

    def test_noCells(self):
        self.assertEqual(5, self.g.NOC_X)
        self.assertEqual(2, self.g.NOC_Y)


class test_grid2D_areas(unittest.TestCase):
    def setUp(self):
        x = axis([0, 1, 3, 5, 7])
        y = axis([0, 2, 5, 9, 14])
        self.g = grid2D(x, y)
        self.areas = self.g.calcCellAreas()

    def test_areas(self):
        self.assertEqual(2.0, self.areas[0, 0])
        self.assertEqual(8.0, self.areas[1, 2])

    def test_areaShape(self):
        self.assertEqual(4, self.areas.shape[0])
        self.assertEqual(4, self.areas.shape[1])


class test_grid2D_centerGrid(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        self.g = grid2D(x, y)
        self.g = self.g.createCenterGrid()

    def test_coords(self):
        self.assertEqual(-4.5, self.g.axis_x.coordsEdges[0])
        self.assertEqual(-3.0, self.g.axis_y.coordsEdges[0])

    def test_noEdges(self):
        self.assertEqual(10, self.g.NOE_X)
        self.assertEqual(4, self.g.NOE_Y)

    def test_noCells(self):
        self.assertEqual(9, self.g.NOC_X)
        self.assertEqual(3, self.g.NOC_Y)

class test_grid2D_extended(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        self.g = grid2D(x, y)
        noCellsX = [1,2]
        noCellsY = [3,4]
        self.g = self.g.createExtended(noCellsX, noCellsY)

    def test_coords(self):
        self.assertEqual(-6.0, self.g.axis_x.coordsEdges[0])
        self.assertEqual(-10.0, self.g.axis_y.coordsEdges[0])

    def test_noEdges(self):
        self.assertEqual(14, self.g.NOE_X)
        self.assertEqual(12, self.g.NOE_Y)

    def test_noCells(self):
        self.assertEqual(13, self.g.NOC_X)
        self.assertEqual(11, self.g.NOC_Y)

class test_grid2D_regularity(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        z = axis(numpy.array([1.0, 2.0, 4.0, 8.0, 14.0, 22.0]))
        self.gReg = grid2D(x, y)
        self.gCart = grid2D(x, x)
        self.gNonUni = grid2D(x, z)

    def test_regular(self):
        self.assertTrue(self.gReg.isRegular())
        self.assertTrue(self.gCart.isRegular())
        self.assertFalse(self.gNonUni.isRegular())

    def test_cartesian(self):
        self.assertFalse(self.gReg.isCartesian())
        self.assertTrue(self.gCart.isCartesian())
        self.assertFalse(self.gNonUni.isCartesian())

class test_grid3D_basic(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        z = axis(numpy.arange(-3.0, 12.0 + 3.0, 3.0))
        self.g = grid3D(x, y, z)

    def test_noEdges(self):
        self.assertEqual(11, self.g.NOE_X)
        self.assertEqual(5, self.g.NOE_Y)
        self.assertEqual(6, self.g.NOE_Z)

    def test_noCells(self):
        self.assertEqual(10, self.g.NOC_X)
        self.assertEqual(4, self.g.NOC_Y)
        self.assertEqual(5, self.g.NOC_Z)

    def test_findCoordEdge(self):
        p = pointCart3D([0.0, 0.0, 0.0])
        idx = self.g.findCoordsEdgeIdx(p)
        self.assertEqual(5, idx.i)
        self.assertEqual(2, idx.j)
        self.assertEqual(1, idx.k)

    def test_findCoordCenter(self):
        p = pointCart3D([0.0, 0.0, 0.0])
        idx = self.g.findCoordsCenterIdx(p)
        self.assertEqual(4, idx.i)
        self.assertEqual(1, idx.j)
        self.assertEqual(0, idx.k)

    def test_edgeBounds(self):
        pA = pointCart3D([0.0, 0.0, 0.0])
        pB = pointCart3D([10.0, 0.0, 0.0])
        self.assertEqual(True, self.g.isCoordsInEdgeBounds(pA))
        self.assertEqual(False, self.g.isCoordsInEdgeBounds(pB))

    def test_centerBounds(self):
        pA = pointCart3D([0.0, 0.0, 0.0])
        pB = pointCart3D([10.0, 0.0, 0.0])
        self.assertEqual(True, self.g.isCoordsInCenterBounds(pA))
        self.assertEqual(False, self.g.isCoordsInCenterBounds(pB))

    def test_edgeCoords(self):
        p = self.g.getCoordsEdge([1, 2, 3])
        self.assertEqual(-4.0, p.x)
        self.assertEqual(0.0, p.y)
        self.assertEqual(6.0, p.z)

    def test_centerCoords(self):
        p = self.g.getCoordsCenter([1, 2, 3])
        self.assertEqual(-3.5, p.x)
        self.assertEqual(1.0, p.y)
        self.assertEqual(7.5, p.z)

    def test_BoundingBox(self):
        coordsStart, coordsStop = self.g.getCoordsBounds()
        self.assertAlmostEquals(-5.0, coordsStart.x, 1)
        self.assertAlmostEquals(-4.0, coordsStart.y, 1)
        self.assertAlmostEquals(-3.0, coordsStart.z, 1)
        self.assertAlmostEquals(5.0, coordsStop.x, 1)
        self.assertAlmostEquals(4.0, coordsStop.y, 1)
        self.assertAlmostEquals(12.0, coordsStop.z, 1)


class test_grid3D_shift(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        z = axis(numpy.arange(-3.0, 12.0 + 3.0, 3.0))
        self.g = grid3D(x, y, z)
        self.g.shiftGrid([5, 4, 3])

    def test_coords(self):
        self.assertEqual(0.0, self.g.axis_x.coordsEdges[0])
        self.assertEqual(0.0, self.g.axis_y.coordsEdges[0])
        self.assertEqual(0.0, self.g.axis_z.coordsEdges[0])

    def test_noEdges(self):
        self.assertEqual(11, self.g.NOE_X)
        self.assertEqual(5, self.g.NOE_Y)
        self.assertEqual(6, self.g.NOE_Z)

    def test_noCells(self):
        self.assertEqual(10, self.g.NOC_X)
        self.assertEqual(4, self.g.NOC_Y)
        self.assertEqual(5, self.g.NOC_Z)

    def test_findCoordEdge(self):
        p = pointCart3D([10.0, 8.0, 6.0])
        idx = self.g.findCoordsEdgeIdx(p)
        self.assertEqual(10, idx.i)
        self.assertEqual(4, idx.j)
        self.assertEqual(2, idx.k)

    def test_findCoordCenter(self):
        p = pointCart3D([8.0, 4.5, 6.0])
        idx = self.g.findCoordsCenterIdx(p)
        self.assertEqual(7, idx.i)
        self.assertEqual(2, idx.j)
        self.assertEqual(1, idx.k)


class test_grid3D_subset(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        z = axis(numpy.arange(-3.0, 12.0 + 3.0, 3.0))
        self.g = grid3D(x, y, z)
        self.g = self.g.createSubset([0, 0, 0], [5, 4, 12])

    def test_coords(self):
        self.assertEqual(0.0, self.g.axis_x.coordsEdges[0])
        self.assertEqual(0.0, self.g.axis_y.coordsEdges[0])
        self.assertEqual(0.0, self.g.axis_z.coordsEdges[0])

    def test_noEdges(self):
        self.assertEqual(6, self.g.NOE_X)
        self.assertEqual(3, self.g.NOE_Y)
        self.assertEqual(5, self.g.NOE_Z)

    def test_noCells(self):
        self.assertEqual(5, self.g.NOC_X)
        self.assertEqual(2, self.g.NOC_Y)
        self.assertEqual(4, self.g.NOC_Z)


class test_grid3D_volumes(unittest.TestCase):
    def setUp(self):
        x = axis([0, 1, 3, 5, 7])
        y = axis([0, 2, 5, 9, 14])
        z = axis([0, 3, 7, 12, 18])
        self.g = grid3D(x, y, z)
        self.volumes = self.g.calcCellVolumes()

    def test_volumes(self):
        self.assertEqual(6.0, self.volumes[0, 0, 0])
        self.assertEqual(48.0, self.volumes[1, 2, 3])

    def test_volumesShape(self):
        self.assertEqual(4, self.volumes.shape[0])
        self.assertEqual(4, self.volumes.shape[1])
        self.assertEqual(4, self.volumes.shape[2])

class test_grid3D_centerGrid(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        z = axis(numpy.arange(-3.0, 12.0 + 3.0, 3.0))
        self.g = grid3D(x, y, z)
        self.g = self.g.createCenterGrid()

    def test_coords(self):
        self.assertEqual(-4.5, self.g.axis_x.coordsEdges[0])
        self.assertEqual(-3.0, self.g.axis_y.coordsEdges[0])
        self.assertEqual(-1.5, self.g.axis_z.coordsEdges[0])

    def test_noEdges(self):
        self.assertEqual(10, self.g.NOE_X)
        self.assertEqual(4, self.g.NOE_Y)
        self.assertEqual(5, self.g.NOE_Z)

    def test_noCells(self):
        self.assertEqual(9, self.g.NOC_X)
        self.assertEqual(3, self.g.NOC_Y)
        self.assertEqual(4, self.g.NOC_Z)

class test_grid3D_extended(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        z = axis(numpy.arange(-3.0, 12.0 + 3.0, 3.0))
        self.g = grid3D(x, y, z)
        noCellsX = [1,2]
        noCellsY = [3,4]
        noCellsZ = [5,6]
        self.g = self.g.createExtended(noCellsX, noCellsY, noCellsZ)

    def test_coords(self):
        self.assertEqual(-6.0, self.g.axis_x.coordsEdges[0])
        self.assertEqual(-10.0, self.g.axis_y.coordsEdges[0])
        self.assertEqual(-18.0, self.g.axis_z.coordsEdges[0])

    def test_noEdges(self):
        self.assertEqual(14, self.g.NOE_X)
        self.assertEqual(12, self.g.NOE_Y)
        self.assertEqual(17, self.g.NOE_Z)

    def test_noCells(self):
        self.assertEqual(13, self.g.NOC_X)
        self.assertEqual(11, self.g.NOC_Y)
        self.assertEqual(16, self.g.NOC_Z)

class test_grid3D_regularity(unittest.TestCase):
    def setUp(self):
        x = axis(numpy.arange(-5.0, 5.0 + 1.0, 1.0))
        y = axis(numpy.arange(-4.0, 4.0 + 2.0, 2.0))
        z = axis(numpy.array([1.0, 2.0, 4.0, 8.0, 14.0, 22.0]))
        self.gReg = grid2D(x, y, x)
        self.gCart = grid2D(x, x, x)
        self.gNonUni = grid2D(x, z, z)

    def test_regular(self):
        self.assertTrue(self.gReg.isRegular())
        self.assertTrue(self.gCart.isRegular())
        self.assertFalse(self.gNonUni.isRegular())

    def test_cartesian(self):
        self.assertFalse(self.gReg.isCartesian())
        self.assertTrue(self.gCart.isCartesian())
        self.assertFalse(self.gNonUni.isCartesian())

if __name__ == "__main__":
    unittest.main(verbosity=2)
