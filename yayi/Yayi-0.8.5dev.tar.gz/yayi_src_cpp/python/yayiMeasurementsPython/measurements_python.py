#!/usr/bin/env python2.3
#  -*- coding=UTF-8 -*-

import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))

from common_test import *
import YayiImageCorePython as YAI
import YayiIOPython as YAIO
import YayiMeasurementsPython as YAMEAS

class MeasurementsTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    pass

  def test1(self):
    im = YAIO.readPNG(os.path.join(test_data_path, "release-grosse bouche.png"))
    hist = YAMEAS.MeasHistogram(im)
    
    # counting the number of bins (known for this image)
    self.assertEqual(len(hist), 21304, 'bad number of colors in the histogram : ' + str(len(hist)) + ' != 21304')

    # Counting the number of elements in each bin
    j = sum(i[1] for i in hist)
    
    self.assertEqual(j, im.Size[0] * im.Size[1], 'bad total count for the histogram')
    

def suite():
  l = []
  for i in [MeasurementsTestCase]:
    suite = unittest.TestLoader().loadTestsFromTestCase(i)
    l.append(suite)

  return unittest.TestSuite(l)  
  
  
if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
