#  -*- coding=UTF-8 -*-

import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))

from common_test import *
import YayiImageCorePython as YAI
import YayiLowLevelMorphologyPython as YALLM
import YayiStructuringElementPython as SE

class ErosionDilationTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    pass


  def testSimpleErosion(self):
    """Tests the erosion with square structuring element"""
    self.image.SetSize((5, 5))

    self.image.AllocateImage()
    
    self.image.slice[:] = \
    [ 1, 2, 3, 2, 3, \
      1, 2, 4, 2, 1, \
      1, 2, 2, 2, 7, \
      1, 2, 5, 2, 1, \
      1, 0, 7, 1, 1, ]

    image_out = YAI.GetSameImage(self.image)
    YALLM.Erosion(self.image, SE.SESquare2D(), image_out)
    
    theoretical_output = \
    [1, 1, 2, 1, 1, \
     1, 1, 2, 1, 1, \
     1, 1, 2, 1, 1, \
     0, 0, 0, 1, 1, \
     0, 0, 0, 1, 1, ]
    
    self.assertEqual(image_out.slice[:], theoretical_output)
    pass    


def suite():
  l = []
  for i in [ErosionDilationTestCase]:
    suite = unittest.TestLoader().loadTestsFromTestCase(i)
    l.append(suite)

  return unittest.TestSuite(l)
  
if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
