#!/usr/bin/env python2.3
#  -*- coding=UTF-8 -*-

import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))

from common_test import *
import YayiImageCorePython  as YAI
import YayiLabelPython      as YAL
import YayiStructuringElementPython as yaSE

class LabelTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    pass

  def testLabelOneArea(self):
    """Tests the labeling of an "homogeneous area" into a fixed value"""
    self.image.Size = (5, 5)
    self.image.AllocateImage()
    
    image_out = YAI.GetSameImageOf(self.image, YAC.type(YAC.c_scalar, YAC.s_ui16))
    
    # setting image to 0
    self.image.slice[:] = 0
    
    YAL.image_label(self.image, yaSE.SESquare2D(), image_out)
    for i in image_out.pixels:
      self.assertEqual(i, 1)
    pass

  def testLabelTwoAreas(self):
    """Tests the labeling of an "homogeneous area" into a fixed value: two connected components"""
    self.image.Size = (5, 5)
    self.image.AllocateImage()
    
    image_out = YAI.GetSameImageOf(self.image, YAC.type(YAC.c_scalar, YAC.s_ui16))
    
    # setting image to 0
    self.image.slice[:] = 0
    # first pixel to 1
    self.image.slice[0] = 1
    
    YAL.image_label(self.image, yaSE.SESquare2D(), image_out)
    self.assertEqual(image_out.slice[0], 1)
    self.assertEqual(sum(abs(i - 2) for i in image_out.slice[1:]), 0)

    # setting image to 0
    self.image.slice[:] = 0
    # first pixel to 1
    self.image.slice[0] = 1
    # adjacent pixel (diagonal) to 1
    self.image.slice[5+1] = 1

    YAL.image_label(self.image, yaSE.SESquare2D(), image_out)
    self.assertEqual(image_out.slice[0], 1)
    self.assertEqual(image_out.slice[5+1], 1)
    self.assertEqual(sum(abs(i - 2) for i in image_out.slice[1:5]), 0)
    self.assertEqual(sum(abs(i - 2) for i in image_out.slice[7:]), 0)

    pass

  def testLabelNonBlackToList(self):
    """Tests the labeling to a list of list of offsets"""
    self.image.Size = (5, 5)
    self.image.AllocateImage()
    
    # setting image to 0
    self.image.slice[:] = 0
    # first pixel to 1
    self.image.slice[0] = 1
    # adjacent pixel (diagonal) to 1
    self.image.slice[5+1] = 1

    res = YAL.image_label_non_black_to_offset(self.image, yaSE.SESquare2D())
    self.assertEqual(len(res), 1)
    self.assertEqual(len(res[0]), 2)
    self.assertEqual(set(res[0]), set((0, 5+1)))
    pass




def suite():
  l = []
  for i in [LabelTestCase]:
    suite = unittest.TestLoader().loadTestsFromTestCase(i)
    l.append(suite)

  return unittest.TestSuite(l)
  

if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
