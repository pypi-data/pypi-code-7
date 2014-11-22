import numpy
import unittest

from fieldpy.primitives.idx import idx2D, idx3D

class test_idx3D_basic(unittest.TestCase):
	
	def setUp(self):
		self.idxA = idx3D([1, 2, 3])
		self.idxB = idx3D([4, 5, 6])
	
	def test_add_idx3D(self):
		idxC = self.idxA + self.idxB
		self.assertEqual(5, idxC.i)
		self.assertEqual(7, idxC.j)
		self.assertEqual(9, idxC.k)
		
	def test_add_int(self):
		idxC = self.idxA + 1
		self.assertEqual(2, idxC.i)
		self.assertEqual(3, idxC.j)
		self.assertEqual(4, idxC.k)
	
	def test_add_list(self):
		idxC = self.idxA + [4, 5, 6]
		self.assertEqual(5, idxC.i)
		self.assertEqual(7, idxC.j)
		self.assertEqual(9, idxC.k)
	
	def test_add_tuple(self):
		idxC = self.idxA + (4, 5, 6)
		self.assertEqual(5, idxC.i)
		self.assertEqual(7, idxC.j)
		self.assertEqual(9, idxC.k)
		
	def test_sub_idx3D(self):
		idxC = self.idxB - self.idxA
		self.assertEqual(3, idxC.i)
		self.assertEqual(3, idxC.j)
		self.assertEqual(3, idxC.k)
		
	def test_sub_int(self):
		idxC = self.idxA - 1
		self.assertEqual(0, idxC.i)
		self.assertEqual(1, idxC.j)
		self.assertEqual(2, idxC.k)
	
	def test_sub_list(self):
		idxC = self.idxA - [0, 1, 1]
		self.assertEqual(1, idxC.i)
		self.assertEqual(1, idxC.j)
		self.assertEqual(2, idxC.k)
	
	def test_sub_tuple(self):
		idxC = self.idxA - [0, 1, 1]
		self.assertEqual(1, idxC.i)
		self.assertEqual(1, idxC.j)
		self.assertEqual(2, idxC.k)

class test_idx3D_advanced(unittest.TestCase):
	
	def setUp(self):
		self.idxA = idx3D([1, 2, 3])
		self.idxB = idx3D([4, 5, 6])
		
	def test_toList(self):
		lstIJK = self.idxA.toList()
		self.assertEqual(1, lstIJK[0])
		self.assertEqual(2, lstIJK[1])
		self.assertEqual(3, lstIJK[2])
		
	def test_toTuple(self):
		tupIJK = self.idxA.toTuple()
		self.assertEqual(1, tupIJK[0])
		self.assertEqual(2, tupIJK[1])
		self.assertEqual(3, tupIJK[2])
	
	def test_fromList(self):
		idx = idx3D([1, 2, 3])
		self.assertEqual(1, idx.i)
		self.assertEqual(2, idx.j)
		self.assertEqual(3, idx.k)

	def test_fromTuple(self):
		idx = idx3D((1, 2, 3))
		self.assertEqual(1, idx.i)
		self.assertEqual(2, idx.j)
		self.assertEqual(3, idx.k)
		
	def test_fromNumPy(self):
		idx = idx3D(numpy.array([1, 2, 3]))
		self.assertEqual(1, idx.i)
		self.assertEqual(2, idx.j)
		self.assertEqual(3, idx.k)

	def test_fromidx3D(self):
		idx = idx3D(idx3D([1, 2, 3]))
		self.assertEqual(1, idx.i)
		self.assertEqual(2, idx.j)
		self.assertEqual(3, idx.k)

	def test_equal(self):
		self.assertEqual(True, self.idxA == self.idxA)
		self.assertEqual(False, self.idxA == self.idxB)

class test_idx2D_basic(unittest.TestCase):
	
	def setUp(self):
		self.idxA = idx2D([1, 2])
		self.idxB = idx2D([4, 5])
	
	def test_add_idx2D(self):
		idxC = self.idxA + self.idxB
		self.assertEqual(5, idxC.i)
		self.assertEqual(7, idxC.j)
		
	def test_add_int(self):
		idxC = self.idxA + 1
		self.assertEqual(2, idxC.i)
		self.assertEqual(3, idxC.j)
	
	def test_add_list(self):
		idxC = self.idxA + [4, 5]
		self.assertEqual(5, idxC.i)
		self.assertEqual(7, idxC.j)
	
	def test_add_tuple(self):
		idxC = self.idxA + (4, 5)
		self.assertEqual(5, idxC.i)
		self.assertEqual(7, idxC.j)
		
	def test_sub_idx2D(self):
		idxC = self.idxB - self.idxA
		self.assertEqual(3, idxC.i)
		self.assertEqual(3, idxC.j)
		
	def test_sub_int(self):
		idxC = self.idxA - 1
		self.assertEqual(0, idxC.i)
		self.assertEqual(1, idxC.j)
	
	def test_sub_list(self):
		idxC = self.idxA - [0, 1]
		self.assertEqual(1, idxC.i)
		self.assertEqual(1, idxC.j)
	
	def test_sub_tuple(self):
		idxC = self.idxA - [0, 1]
		self.assertEqual(1, idxC.i)
		self.assertEqual(1, idxC.j)

class test_idx2D_advanced(unittest.TestCase):
	
	def setUp(self):
		self.idxA = idx2D([1, 2])
		self.idxB = idx2D([4, 5])
		
	def test_toList(self):
		lstIJK = self.idxA.toList()
		self.assertEqual(1, lstIJK[0])
		self.assertEqual(2, lstIJK[1])
		
	def test_toTuple(self):
		tupIJK = self.idxA.toTuple()
		self.assertEqual(1, tupIJK[0])
		self.assertEqual(2, tupIJK[1])
	
	def test_fromList(self):
		idx = idx2D([1, 2])
		self.assertEqual(1, idx.i)
		self.assertEqual(2, idx.j)

	def test_fromTuple(self):
		idx = idx2D((1, 2))
		self.assertEqual(1, idx.i)
		self.assertEqual(2, idx.j)
		
	def test_fromNumPy(self):
		idx = idx2D(numpy.array([1, 2]))
		self.assertEqual(1, idx.i)
		self.assertEqual(2, idx.j)

	def test_fromidx2D(self):
		idx = idx2D(idx2D([1, 2]))
		self.assertEqual(1, idx.i)
		self.assertEqual(2, idx.j)

	def test_equal(self):
		self.assertEqual(True, self.idxA == self.idxA)
		self.assertEqual(False, self.idxA == self.idxB)

if __name__ == "__main__":
	unittest.main(verbosity=2)
