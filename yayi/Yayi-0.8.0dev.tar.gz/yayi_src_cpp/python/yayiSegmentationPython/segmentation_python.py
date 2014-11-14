#!/usr/bin/env python2.3
#  -*- coding=UTF-8 -*-


import os, sys, unittest, exceptions, tempfile

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))

from common_test import *
import YayiImageCorePython as YAI
import YayiIOPython as YAIO
import YayiPixelProcessingPython as YAPIX
import YayiStructuringElementPython as YASE
import YayiSegmentationPython as YASEGM
import YayiLowLevelMorphologyPython as YAMM


class SegmentationTestCase(unittest.TestCase):
  def setUp(self):
    self.imname = os.path.join(os.path.split(__file__)[0], os.pardir, os.pardir, "coreTests", "yayiTestData", "release-grosse bouche.jpg")
    im = YAIO.readJPG(self.imname)
    self.image = YAI.GetSameImageOf(im, YAC.type(YAC.c_scalar, YAC.s_ui8))
    imagetmp = YAI.GetSameImage(self.image)
    
    # keeping only channel 0 (red)
    YAPIX.CopyOneChannel(im, 0, imagetmp)
    
    # computing the gradient on the image, hex structuring element
    YAMM.Gradient(imagetmp, YASE.SEHex2D(), self.image)
    
  def tearDown(self):
    pass

  def test1(self):
    self.out_im = YAI.GetSameImageOf(self.image, YAC.type(YAC.c_scalar, YAC.s_ui16))

    # the watershed itself
    YASEGM.IsotropicWatershed(self.image, YASE.SEHex2D(), self.out_im)
    outfile = tempfile.mkstemp(os.path.split(self.imname)[1])
    
    # writing the result
    YAIO.writePNG(outfile[1], self.out_im)
    
    outfile = tempfile.mkstemp(os.path.split(self.imname)[1])
    # outputting the gradient image
    YAIO.writePNG(outfile[1], self.image)
    

def suite():
  suite = unittest.TestSuite()
  suite.addTest(SegmentationTestCase('test1'))

  return suite
  
  
if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
