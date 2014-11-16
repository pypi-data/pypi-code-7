#!/usr/bin/env python2.3
#  -*- coding=UTF-8 -*-

import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))

from common_test import *
import YayiImageCorePython as YAI
import YayiIOPython as YAIO
import YayiStructuringElementPython as YASE
import YayiReconstructionPython as YACURRENT

class ReconstructionTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    pass

  def testReconstruction1(self):
    self.image.Size = (5, 5)
    self.image.AllocateImage()
    
    self.image.slice[:] = \
    [ 1, 2, 3, 2, 3, \
      1, 2, 4, 2, 1, \
      1, 2, 2, 2, 7, \
      1, 2, 5, 2, 1, \
      1, 0, 7, 1, 1, ]
    
    image_mark = YAI.GetSameImage(self.image)
    image_mark.slice[:] = 0
    image_mark.slice[2*(5+1)] = 7
    
    image_out = YAI.GetSameImage(self.image)
    
    YACURRENT.OpeningByReconstruction(image_mark, self.image, YASE.SESquare2D(), image_out)
    
    theoretical_output = \
    [1, 2, 2, 2, 2, \
     1, 2, 2, 2, 1, \
     1, 2, 2, 2, 2, \
     1, 2, 2, 2, 1, \
     1, 0, 2, 1, 1, ]
    
    self.assertEqual(image_out.slice[:], theoretical_output)
    pass
    

def suite():
  l = []
  for i in [ReconstructionTestCase]:
    suite = unittest.TestLoader().loadTestsFromTestCase(i)
    l.append(suite)

  return unittest.TestSuite(l)  
  
  
if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
