import numpy
import unittest

from fieldpy.primitives.axis import axis


class test_axis_basic(unittest.TestCase):
    def setUp(self):
        self.ax = axis(numpy.arange(-10.0, 10.0 + 0.5, 0.5))

    def test_noEdges(self):
        self.assertEqual(41, self.ax.noEdges)
        self.assertEqual(41, len(self.ax))

    def test_noCells(self):
        self.assertEqual(40, self.ax.noCells)

    def test_widths(self):
        self.assertEqual(0.5, self.ax.widths[0])
        self.assertEqual(0.5, self.ax.widths[self.ax.noCells - 1])

    def test_centers(self):
        self.assertEqual(-9.75, self.ax.coordsCenters[0])
        self.assertEqual(9.75, self.ax.coordsCenters[self.ax.noCells - 1])

    def test_edgeBounds(self):
        self.assertEqual(True, self.ax.isCoordInEdgeBounds(-9))
        self.assertEqual(True, self.ax.isCoordInEdgeBounds(9))
        self.assertEqual(False, self.ax.isCoordInEdgeBounds(-11))
        self.assertEqual(False, self.ax.isCoordInEdgeBounds(11))

    def test_centerBounds(self):
        self.assertEqual(True, self.ax.isCoordInCenterBounds(-9))
        self.assertEqual(True, self.ax.isCoordInCenterBounds(9))
        self.assertEqual(False, self.ax.isCoordInCenterBounds(-10))
        self.assertEqual(False, self.ax.isCoordInCenterBounds(10))

    def test_findCoordEdgeIdx(self):
        self.assertEqual(30, self.ax.findCoordEdgeIdx(5))
        self.assertEqual(40, self.ax.findCoordEdgeIdx(15))
        self.assertEqual(10, self.ax.findCoordEdgeIdx(-5))
        self.assertEqual(0, self.ax.findCoordEdgeIdx(-15))
        self.assertEqual(31, self.ax.findCoordEdgeIdx(5.5))
        self.assertEqual(9, self.ax.findCoordEdgeIdx(-5.5))

    def test_findCoordCenterIdx(self):
        self.assertEqual(29, self.ax.findCoordCenterIdx(5))
        self.assertEqual(39, self.ax.findCoordCenterIdx(15))
        self.assertEqual(9, self.ax.findCoordCenterIdx(-5))
        self.assertEqual(0, self.ax.findCoordCenterIdx(-15))
        self.assertEqual(30, self.ax.findCoordCenterIdx(5.5))
        self.assertEqual(8, self.ax.findCoordCenterIdx(-5.5))

    def test_findMinWidth(self):
        self.assertEqual(0.5, self.ax.findMinWidth())

    def test_findMaxWidth(self):
        self.assertEqual(0.5, self.ax.findMaxWidth())


class test_axis_shift(unittest.TestCase):
    def setUp(self):
        self.ax = axis(numpy.arange(-10.0, 10.0 + 0.5, 0.5))
        self.ax.shiftAxis(10.0)

    def test_noEdges(self):
        self.assertEqual(41, self.ax.noEdges)

    def test_noCells(self):
        self.assertEqual(40, self.ax.noCells)

    def test_widths(self):
        self.assertEqual(0.5, self.ax.widths[0])
        self.assertEqual(0.5, self.ax.widths[self.ax.noCells - 1])

    def test_centers(self):
        self.assertEqual(0.25, self.ax.coordsCenters[0])
        self.assertEqual(19.75, self.ax.coordsCenters[self.ax.noCells - 1])

    def test_edgeBounds(self):
        self.assertEqual(False, self.ax.isCoordInEdgeBounds(-9))
        self.assertEqual(True, self.ax.isCoordInEdgeBounds(19))
        self.assertEqual(True, self.ax.isCoordInEdgeBounds(0))
        self.assertEqual(False, self.ax.isCoordInEdgeBounds(21))

    def test_centerBounds(self):
        self.assertEqual(False, self.ax.isCoordInCenterBounds(-9))
        self.assertEqual(True, self.ax.isCoordInCenterBounds(19))
        self.assertEqual(True, self.ax.isCoordInCenterBounds(0.5))
        self.assertEqual(False, self.ax.isCoordInCenterBounds(21))

    def test_findCoordEdgeIdx(self):
        self.assertEqual(10, self.ax.findCoordEdgeIdx(5))
        self.assertEqual(30, self.ax.findCoordEdgeIdx(15))
        self.assertEqual(0, self.ax.findCoordEdgeIdx(-5))
        self.assertEqual(40, self.ax.findCoordEdgeIdx(25))
        self.assertEqual(11, self.ax.findCoordEdgeIdx(5.5))
        self.assertEqual(29, self.ax.findCoordEdgeIdx(14.5))


class test_axis_subset(unittest.TestCase):
    def setUp(self):
        self.ax = axis(numpy.arange(-10.0, 10.0 + 0.5, 0.5))

    def test_StartInStopIn(self):
        ax2 = self.ax.createSubset(-5, 5)
        self.assertEqual(21, ax2.noEdges)
        ax3 = self.ax.createSubset(-5.25, 5.25)
        self.assertEqual(22, ax3.noEdges)

    def test_StartOutStopIn(self):
        ax2 = self.ax.createSubset(-15, 5)
        self.assertEqual(31, ax2.noEdges)

    def test_StartInStopOut(self):
        ax2 = self.ax.createSubset(-5, 15)
        self.assertEqual(31, ax2.noEdges)


class test_axis_extend_fixedWidth(unittest.TestCase):
    def setUp(self):
        self.ax = axis(numpy.arange(-10.0, 10.0 + 0.5, 0.5))

    def test_Left(self):
        noCells = 5
        ax2 = self.ax.createExtended("left", noCells)
        self.assertEqual(self.ax.noCells+noCells, ax2.noCells)
        self.assertEqual(-12.5 , ax2.coordsEdges[0])
        self.assertEqual(self.ax.coordsEdges[-1] , ax2.coordsEdges[-1])

    def test_Right(self):
        noCells = 4
        ax2 = self.ax.createExtended("right", noCells)
        self.assertEqual(self.ax.noCells+noCells, ax2.noCells)
        self.assertEqual(12.0 , ax2.coordsEdges[-1])
        self.assertEqual(self.ax.coordsEdges[0] , ax2.coordsEdges[0])

    def test_Both_uni(self):
        noCells = 6
        ax2 = self.ax.createExtended("both", noCells)
        self.assertEqual(self.ax.noCells+noCells+noCells, ax2.noCells)
        self.assertEqual(-13.0 , ax2.coordsEdges[0])
        self.assertEqual(13.0 , ax2.coordsEdges[-1])

    def test_Both_nonuni(self):
        noCells = [4,5]
        ax2 = self.ax.createExtended("both", noCells)
        self.assertEqual(self.ax.noCells+noCells[0]+noCells[1], ax2.noCells)
        self.assertEqual(-12.0 , ax2.coordsEdges[0])
        self.assertEqual(12.5 , ax2.coordsEdges[-1])

class test_axis_extend_customWidth(unittest.TestCase):
    def setUp(self):
        self.ax = axis(numpy.arange(-10.0, 10.0 + 0.5, 0.5))

    def test_Left(self):
        noCells = 5
        widths = 1.0
        ax2 = self.ax.createExtended("left", noCells, widths)
        self.assertEqual(self.ax.noCells+noCells, ax2.noCells)
        self.assertEqual(-15.0 , ax2.coordsEdges[0])
        self.assertEqual(self.ax.coordsEdges[-1] , ax2.coordsEdges[-1])

    def test_Right(self):
        noCells = 4
        widths = 2.0
        ax2 = self.ax.createExtended("right", noCells, widths)
        self.assertEqual(self.ax.noCells+noCells, ax2.noCells)
        self.assertEqual(18.0 , ax2.coordsEdges[-1])
        self.assertEqual(self.ax.coordsEdges[0] , ax2.coordsEdges[0])

    def test_Both_uni(self):
        noCells = 6
        widths = [1.5, 2.5]
        ax2 = self.ax.createExtended("both", noCells, widths)
        self.assertEqual(self.ax.noCells+noCells+noCells, ax2.noCells)
        self.assertEqual(-19.0 , ax2.coordsEdges[0])
        self.assertEqual(25.0 , ax2.coordsEdges[-1])

    def test_Both_nonuni(self):
        noCells = [4,5]
        widths = 1.0
        ax2 = self.ax.createExtended("both", noCells, widths)
        self.assertEqual(self.ax.noCells+noCells[0]+noCells[1], ax2.noCells)
        self.assertEqual(-14.0 , ax2.coordsEdges[0])
        self.assertEqual(15.0 , ax2.coordsEdges[-1])

if __name__ == "__main__":
    unittest.main(verbosity=2)