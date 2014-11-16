#!/usr/bin/env python2.3
# -*- coding=UTF-8 -*-


import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))

from common_test import *
import YayiImageCorePython as YAI
import YayiIOPython as YAIO
import YayiNeighborhoodProcessingPython as YACURRENT

class NeighborhoodProcessingTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    pass

  def test1(self):
    pass
    

def suite():
  l = []
  for i in [NeighborhoodProcessingTestCase]:
    suite = unittest.TestLoader().loadTestsFromTestCase(i)
    l.append(suite)

  return unittest.TestSuite(l)  
  
  
if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)