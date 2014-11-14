#!/usr/bin/env python2.3
#  -*- coding=UTF-8 -*-

import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))
from common_test import *
import YayiIOPython               as yaIO
import YayiImageCorePython        as yaCORE
import YayiPixelProcessingPython  as yaP



class ImageIOCase(unittest.TestCase):
  def setUp(self):
    self.image = yaCORE.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    pass
    
  def testJPGIO(self):
    """Testing JPG I/O functions"""
    im = yaIO.readJPG(os.path.join(test_data_path, "release-grosse bouche.jpg"))
    self.assertEqual(im.Size, (450,600))
    outfile = os.tmpnam() + "release-grosse bouche.jpg"
    yaIO.writeJPG(outfile, im)
    os.remove(outfile) 

  def testPNGIO(self):
    """Testing PNG I/O functions"""
    im = yaIO.readPNG(os.path.join(test_data_path, "release-grosse bouche.png"))
    self.assertEqual(im.Size, (450,600))
    outfile = os.tmpnam() + "release-grosse bouche.png"
    yaIO.writePNG(outfile, im)
    os.remove(outfile) 
  
  def testHDF5IO(self):
    im = yaIO.readHDF5(os.path.join(os.path.split(__file__)[0], os.pardir, os.pardir, "coreTests", "yayiTestData", "debug_HDF5.h5"), "bla")
    #im = yaIO.readHDF5(os.path.join(os.path.split(__file__)[0], os.pardir, os.pardir, "coreTests", "yayiTestData", "wt_K_4ora_colchcine60_RAM2.h5"), "/rawdata/stitched_weighted_ch0/")
    #im = yaIO.readHDF5("/home/enficiau/wt_K_4ora_colchcine60_RAM2.h5")
    self.assertEqual(im.pixel((5,4,2)).value, 5*4*2);

    for z in range(10):
      for y in range(10):
        for x in range(10):
          self.assertEqual(im.pixel((x,y,z)).value, x*y*z);

  def testNumpy(self):
    """Tests numpy related functions (optional)"""
    import numpy as np
    current_array = np.array([[(i + k) % (k + 1) for i in range(30)] for k in range(17)], np.uint8)
    im = yaIO.image_from_numpy(current_array)
    self.assertEqual(im.Size, (30, 17), 'error on the size of the read image : ' + str(im.Size) + ' != ' + str((30, 17)))
    self.assertEqual(im.pixel((10, 5)), (10 + 5) % (5 + 1), 'error on the value of the image at position (10, 5) ' + str(im.pixel((10, 5))) + ' != ' + str((10 + 5) % (5 + 1)))

    current_array2 = yaIO.image_to_numpy(im)
    
    # check consistency
    self.assertTrue(np.all(np.equal(current_array, current_array2)), 'something wrong:wiews are not identical')
    
    # check view
    v = current_array2[10, 10]
    current_array2[10,10] = v - 1
    self.assertEqual(im.pixel((10,10)), v-1, 'the array does not seem to be a "view" of the image content')
    current_array2[10,10] = v
    
    # check lifetime
    del im
    self.assertTrue(np.all(np.equal(current_array, current_array2)), 'something wrong')
    del current_array2
    
    # warning: if image is unallocated with FreeImage, then things are likely to crash :)
    
    self.assertRaises(Exception, yaIO.image_from_numpy([i for i in range(20)]))
    try:
      im = yaIO.image_from_numpy([i for i in range(20)])
      self.assert_(False, "Should have thrown an exception")
    except Exception,e:
      print "Exception caught ok!", e
      pass

def suite():
  # the set of test is dependent of the command line, keep it this way
  suite = unittest.TestSuite()
  
  suite.addTest(ImageIOCase('testJPGIO'))
  suite.addTest(ImageIOCase('testPNGIO'))
  if(sys.argv.count('HDF5')):
    suite.addTest(ImageIOCase('testHDF5IO'))
  if(sys.argv.count('NUMPY')):
    suite.addTest(ImageIOCase('testNumpy'))
  return suite


if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)


