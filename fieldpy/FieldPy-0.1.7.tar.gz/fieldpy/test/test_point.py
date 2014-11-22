import numpy
import unittest

from fieldpy.primitives.point import pointCart2D, pointCart3D

class test_pointCart3D_basic(unittest.TestCase):
	
	def setUp(self):
		self.pA = pointCart3D([1.0, 2.0, 3.0])
		self.pB = pointCart3D([4.0, 5.0, 6.0])
	
	def test_add_pointCart3D(self):
		pC = self.pA + self.pB
		self.assertEqual(5.0, pC.x)
		self.assertEqual(7.0, pC.y)
		self.assertEqual(9.0, pC.z)
		
	def test_add_float(self):
		pC = self.pA + 1.5
		self.assertEqual(2.5, pC.x)
		self.assertEqual(3.5, pC.y)
		self.assertEqual(4.5, pC.z)
		
	def test_add_int(self):
		pC = self.pA + 1
		self.assertEqual(2.0, pC.x)
		self.assertEqual(3.0, pC.y)
		self.assertEqual(4.0, pC.z)
	
	def test_add_list(self):
		pC = self.pA + [4.0, 5.0, 6.0]
		self.assertEqual(5.0, pC.x)
		self.assertEqual(7.0, pC.y)
		self.assertEqual(9.0, pC.z)
	
	def test_add_tuple(self):
		pC = self.pA + (4.0, 5.0, 6.0)
		self.assertEqual(5.0, pC.x)
		self.assertEqual(7.0, pC.y)
		self.assertEqual(9.0, pC.z)
		
	def test_sub_pointCart3D(self):
		pC = self.pA - self.pB
		self.assertEqual(-3.0, pC.x)
		self.assertEqual(-3.0, pC.y)
		self.assertEqual(-3.0, pC.z)
		
	def test_sub_float(self):
		pC = self.pA - 1.5
		self.assertEqual(-0.5, pC.x)
		self.assertEqual(0.5, pC.y)
		self.assertEqual(1.5, pC.z)
		
	def test_sub_int(self):
		pC = self.pA - 1
		self.assertEqual(0.0, pC.x)
		self.assertEqual(1.0, pC.y)
		self.assertEqual(2.0, pC.z)
	
	def test_sub_list(self):
		pC = self.pA - [4.0, 5.0, 6.0]
		self.assertEqual(-3.0, pC.x)
		self.assertEqual(-3.0, pC.y)
		self.assertEqual(-3.0, pC.z)
	
	def test_sub_tuple(self):
		pC = self.pA - (4.0, 5.0, 6.0)
		self.assertEqual(-3.0, pC.x)
		self.assertEqual(-3.0, pC.y)
		self.assertEqual(-3.0, pC.z)
		
	def test_mul_pointCart3D(self):
		pC = self.pA * self.pB
		self.assertEqual(4.0, pC.x)
		self.assertEqual(10.0, pC.y)
		self.assertEqual(18.0, pC.z)
		
	def test_mul_float(self):
		pC = self.pA * 5.0
		self.assertEqual(5.0, pC.x)
		self.assertEqual(10.0, pC.y)
		self.assertEqual(15.0, pC.z)
		
	def test_mul_int(self):
		pC = self.pA * 2
		self.assertEqual(2.0, pC.x)
		self.assertEqual(4.0, pC.y)
		self.assertEqual(6.0, pC.z)
	
	def test_mul_list(self):
		pC = self.pA * [4.0, 5.0, 6.0]
		self.assertEqual(4.0, pC.x)
		self.assertEqual(10.0, pC.y)
		self.assertEqual(18.0, pC.z)
	
	def test_mul_tuple(self):
		pC = self.pA * (4.0, 5.0, 6.0)
		self.assertEqual(4.0, pC.x)
		self.assertEqual(10.0, pC.y)
		self.assertEqual(18.0, pC.z)

	def test_div_pointCart3D(self):
		pC = self.pA / self.pB
		self.assertEqual(0.25, pC.x)
		self.assertEqual(0.4, pC.y)
		self.assertEqual(0.5, pC.z)
		
	def test_div_float(self):
		pC = self.pA / 2.0
		self.assertEqual(0.5, pC.x)
		self.assertEqual(1.0, pC.y)
		self.assertEqual(1.5, pC.z)
		
	def test_div_int(self):
		pC = self.pA / 4
		self.assertEqual(0.25, pC.x)
		self.assertEqual(0.5, pC.y)
		self.assertEqual(0.75, pC.z)
	
	def test_div_list(self):
		pC = self.pA / [4.0, 5.0, 6.0]
		self.assertEqual(0.25, pC.x)
		self.assertEqual(0.4, pC.y)
		self.assertEqual(0.5, pC.z)
	
	def test_div_tuple(self):
		pC = self.pA / (4.0, 5.0, 6.0)
		self.assertEqual(0.25, pC.x)
		self.assertEqual(0.4, pC.y)
		self.assertEqual(0.5, pC.z)
	
	def test_abs(self):
		self.assertAlmostEqual(3.741, abs(self.pA), 2)
	
class test_pointCart3D_advanced(unittest.TestCase):
	
	def setUp(self):
		self.pA = pointCart3D([1.0, 2.0, 3.0])
		self.pB = pointCart3D([4.0, 5.0, 6.0])
		
	def test_toList(self):
		lstXYZ = self.pA.toList()
		self.assertEqual(1.0, lstXYZ[0])
		self.assertEqual(2.0, lstXYZ[1])
		self.assertEqual(3.0, lstXYZ[2])
		
	def test_toTuple(self):
		tupXYZ = self.pA.toTuple()
		self.assertEqual(1.0, tupXYZ[0])
		self.assertEqual(2.0, tupXYZ[1])
		self.assertEqual(3.0, tupXYZ[2])
	
	def test_fromList(self):
		p = pointCart3D([1.0, 2.0, 3.0])
		self.assertEqual(1.0, p.x)
		self.assertEqual(2.0, p.y)
		self.assertEqual(3.0, p.z)

	def test_fromTuple(self):
		p = pointCart3D((1.0, 2.0, 3.0))
		self.assertEqual(1.0, p.x)
		self.assertEqual(2.0, p.y)
		self.assertEqual(3.0, p.z)
		
	def test_fromNumPy(self):
		p = pointCart3D(numpy.array([1.0, 2.0, 3.0]))
		self.assertEqual(1.0, p.x)
		self.assertEqual(2.0, p.y)
		self.assertEqual(3.0, p.z)

	def test_fromPointCart(self):
		p = pointCart3D(pointCart3D([1.0, 2.0, 3.0]))
		self.assertEqual(1.0, p.x)
		self.assertEqual(2.0, p.y)
		self.assertEqual(3.0, p.z)

	def test_equal(self):
		self.assertEqual(True, self.pA == self.pA)
		self.assertEqual(False, self.pA == self.pB)

	def test_calcDistanceSqrd(self):
		self.assertEqual(27.0, pointCart3D.calcDistanceSqrd(self.pA, self.pB))

	def test_calcDistance(self):
		self.assertAlmostEqual(5.196, pointCart3D.calcDistance(self.pA, self.pB), 3)

	def test_calcMidPoint(self):
		p = pointCart3D.calcMidPoint(self.pA, self.pB)
		self.assertEqual(2.5, p.x)
		self.assertEqual(3.5, p.y)
		self.assertEqual(4.5, p.z)

class test_pointCart2D_basic(unittest.TestCase):
	
	def setUp(self):
		self.pA = pointCart2D([1.0, 2.0])
		self.pB = pointCart2D([4.0, 5.0])
	
	def test_add_pointCart3D(self):
		pC = self.pA + self.pB
		self.assertEqual(5.0, pC.x)
		self.assertEqual(7.0, pC.y)
		
	def test_add_float(self):
		pC = self.pA + 1.5
		self.assertEqual(2.5, pC.x)
		self.assertEqual(3.5, pC.y)
		
	def test_add_int(self):
		pC = self.pA + 1
		self.assertEqual(2.0, pC.x)
		self.assertEqual(3.0, pC.y)
	
	def test_add_list(self):
		pC = self.pA + [4.0, 5.0]
		self.assertEqual(5.0, pC.x)
		self.assertEqual(7.0, pC.y)
	
	def test_add_tuple(self):
		pC = self.pA + (4.0, 5.0)
		self.assertEqual(5.0, pC.x)
		self.assertEqual(7.0, pC.y)
		
	def test_sub_pointCart2D(self):
		pC = self.pA - self.pB
		self.assertEqual(-3.0, pC.x)
		self.assertEqual(-3.0, pC.y)
		
	def test_sub_float(self):
		pC = self.pA - 1.5
		self.assertEqual(-0.5, pC.x)
		self.assertEqual(0.5, pC.y)
		
	def test_sub_int(self):
		pC = self.pA - 1
		self.assertEqual(0.0, pC.x)
		self.assertEqual(1.0, pC.y)
	
	def test_sub_list(self):
		pC = self.pA - [4.0, 5.0]
		self.assertEqual(-3.0, pC.x)
		self.assertEqual(-3.0, pC.y)
	
	def test_sub_tuple(self):
		pC = self.pA - (4.0, 5.0)
		self.assertEqual(-3.0, pC.x)
		self.assertEqual(-3.0, pC.y)
		
	def test_mul_pointCart2D(self):
		pC = self.pA * self.pB
		self.assertEqual(4.0, pC.x)
		self.assertEqual(10.0, pC.y)
		
	def test_mul_float(self):
		pC = self.pA * 5.0
		self.assertEqual(5.0, pC.x)
		self.assertEqual(10.0, pC.y)
		
	def test_mul_int(self):
		pC = self.pA * 2
		self.assertEqual(2.0, pC.x)
		self.assertEqual(4.0, pC.y)
	
	def test_mul_list(self):
		pC = self.pA * [4.0, 5.0]
		self.assertEqual(4.0, pC.x)
		self.assertEqual(10.0, pC.y)
	
	def test_mul_tuple(self):
		pC = self.pA * (4.0, 5.0)
		self.assertEqual(4.0, pC.x)
		self.assertEqual(10.0, pC.y)

	def test_div_pointCart3D(self):
		pC = self.pA / self.pB
		self.assertEqual(0.25, pC.x)
		self.assertEqual(0.4, pC.y)
		
	def test_div_float(self):
		pC = self.pA / 2.0
		self.assertEqual(0.5, pC.x)
		self.assertEqual(1.0, pC.y)
		
	def test_div_int(self):
		pC = self.pA / 4
		self.assertEqual(0.25, pC.x)
		self.assertEqual(0.5, pC.y)
	
	def test_div_list(self):
		pC = self.pA / [4.0, 5.0]
		self.assertEqual(0.25, pC.x)
		self.assertEqual(0.4, pC.y)
	
	def test_div_tuple(self):
		pC = self.pA / (4.0, 5.0)
		self.assertEqual(0.25, pC.x)
		self.assertEqual(0.4, pC.y)
	
	def test_abs(self):
		self.assertAlmostEqual(2.236, abs(self.pA), 2)

class test_pointCart2D_advanced(unittest.TestCase):
	
	def setUp(self):
		self.pA = pointCart2D([1.0, 2.0])
		self.pB = pointCart2D([4.0, 5.0])
		
	def test_toList(self):
		lstXYZ = self.pA.toList()
		self.assertEqual(1.0, lstXYZ[0])
		self.assertEqual(2.0, lstXYZ[1])
		
	def test_toTuple(self):
		tupXYZ = self.pA.toTuple()
		self.assertEqual(1.0, tupXYZ[0])
		self.assertEqual(2.0, tupXYZ[1])
	
	def test_fromList(self):
		p = pointCart2D([1.0, 2.0])
		self.assertEqual(1.0, p.x)
		self.assertEqual(2.0, p.y)

	def test_fromTuple(self):
		p = pointCart2D((1.0, 2.0))
		self.assertEqual(1.0, p.x)
		self.assertEqual(2.0, p.y)
		
	def test_fromNumPy(self):
		p = pointCart2D(numpy.array([1.0, 2.0]))
		self.assertEqual(1.0, p.x)
		self.assertEqual(2.0, p.y)
		
	def test_fromPointCart(self):
		p = pointCart2D(pointCart2D([1.0, 2.0]))
		self.assertEqual(1.0, p.x)
		self.assertEqual(2.0, p.y)
		
	def test_equal(self):
		self.assertEqual(True, self.pA == self.pA)
		self.assertEqual(False, self.pA == self.pB)

	def test_calcDistanceSqrd(self):
		self.assertEqual(18.0, pointCart2D.calcDistanceSqrd(self.pA, self.pB))

	def test_calcDistance(self):
		self.assertAlmostEqual(4.24, pointCart2D.calcDistance(self.pA, self.pB), 2)

	def test_calcMidPoint(self):
		p = pointCart2D.calcMidPoint(self.pA, self.pB)
		self.assertEqual(2.5, p.x)
		self.assertEqual(3.5, p.y)

if __name__ == "__main__":
	unittest.main(verbosity=2)
