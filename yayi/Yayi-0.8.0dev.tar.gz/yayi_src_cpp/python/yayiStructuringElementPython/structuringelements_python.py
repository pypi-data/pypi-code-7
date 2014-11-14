#  -*- coding=UTF-8 -*-


# structuring element tests

import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))
from common_test import *
import YayiStructuringElementPython as yaSE
import YayiImageCorePython          as yaCORE

class SECreateCase(unittest.TestCase):
  """Tests the creation of structuring elements and neighborhoods/neighborhood iterators in images (2D/3D)"""

  def setUp(self):
    self.image2D = yaCORE.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)
    self.image3D = yaCORE.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui16), 3)
    
    self.image2D.Size = (10, 10)
    self.image2D.AllocateImage()

    self.image3D.Size = (10, 15, 20)
    self.image3D.AllocateImage()
    
    

  def tearDown(self):
    del self.image2D
    del self.image3D
    
    
  def testCreateSE(self):
    """Tests some structuring elements factories"""
    
    # this is a vertical bar in 2D
    se = yaSE.SEFactory(yaSE.e_set_neighborlist, 2, (0,1, 0,0, 0,-1), yaSE.e_sest_neighborlist_generic_single)
    self.assertIsNotNone(se)

    # this is a two points SE: (0,1, 0) and (0, 0,-1)
    se = yaSE.SEFactory(yaSE.e_set_neighborlist, 3, (0,1, 0,0, 0,-1), yaSE.e_sest_neighborlist_generic_single)
    self.assertIsNotNone(se)

    
  def testStructuringElementComparisons(self):
    """Tests structuring element comparison functions"""
    se = yaSE.SEFactory(yaSE.e_set_neighborlist, 2, (0,1, 0,0, 0,-1), yaSE.e_sest_neighborlist_generic_single)
    self.assertIsNotNone(se)

    self.assertEqual(se, se)
    self.assertTrue(se % se)
    self.assertTrue(se.IsEqualUnordered(se))
    
    
    self.assertNotEqual(se, yaSE.SEHex2D())
    self.assertNotEqual(se, yaSE.SESquare2D())
    self.assertNotEqual(se, yaSE.SESquare2D())
    self.assertTrue(se % yaSE.SESegmentY2D())

    se2 = yaSE.SEFactory(yaSE.e_set_neighborlist, 2, (0,-1, 0,0, 0,1), yaSE.e_sest_neighborlist_generic_single)
    self.assertNotEqual(se, se2)
    self.assertTrue(se % se2)
    
    # check it does not crash
    del se
  
  def testCloneOk(self):
    """Tests (indirectly) the cloning of structuring elements"""
    self.assertEqual(yaSE.SEHex2D().SEType, yaSE.e_set_neighborlist)
    self.assertEqual(yaSE.SEHex2D().SETSubtype, yaSE.e_sest_neighborlist_hexa)
  
  def testNeighborhood(self):
    """Tests the neighborhood creation and behavior functions"""
    se = yaSE.SEFactory(yaSE.e_set_neighborlist, 2, (0,1, 0,0, 0,-1), yaSE.e_sest_neighborlist_generic_single)
    self.assertIsNotNone(se)

    neighbor = yaSE.NeighborhoodFactory(self.image2D, se)
    self.assertIsNotNone(neighbor)
    
    # center
    neighbor.Center((5, 5))
    i = sum([1 for i in neighbor.pixels])
    
    self.assertEqual(i, 3)

    # center close to the borders
    neighbor.Center((5, 0))
    i = sum([1 for i in neighbor.pixels])
    
    self.assertEqual(i, 2)

    # different form of iteration
    it = neighbor.pixels
    i = 0
    while it.has_next():
      i += 1
      it.next()
    
    self.assertEqual(i, 2)


def suite():
  l = []
  for i in [SECreateCase]:
    suite = unittest.TestLoader().loadTestsFromTestCase(i)
    l.append(suite)

  return unittest.TestSuite(l)  

if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)


