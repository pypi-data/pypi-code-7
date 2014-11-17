#!/usr/bin/env python2.3
#  -*- coding=UTF-8 -*-

import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))
from common_test import *
import YayiImageCorePython as YAI

class ImageTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    pass

  def testType(self):
    """Tests the type of the allocated image"""
    self.assertEqual(self.image.DynamicType(), YAC.type(YAC.c_scalar, YAC.s_ui8), 'bad image type :' + str(self.image.DynamicType()))
    self.assertGreater(str(self.image).find(str(YAC.type(YAC.c_scalar, YAC.s_ui8))), -1, 'image seems to have a bad description :' + str(self.image))

  def testDefaultSizeIsNull(self):
    """Test size defaults to null when intanciated (and not garbage)"""
    self.assertEqual(self.image.GetSize(), (0, 0))

  def testDefaultSize(self):
    """Test various size getters/setters"""
    self.image.SetSize((10,10))
    self.assertEqual(self.image.GetSize(), (10, 10))

    self.image.SetSize((20,10))
    self.assertEqual(self.image.GetSize(), (20, 10))

    self.image.Size = (20,11)
    self.assertEqual(self.image.GetSize(), (20, 11))

    self.image.Size = (23,11)
    self.assertEqual(self.image.Size, (23, 11))

    self.assertRaises(exceptions.RuntimeError, self.image.SetSize, (-4,150))
    self.assertRaises(exceptions.RuntimeError, self.image.SetSize, (0,0))

    self.image.AllocateImage()
    self.assertEqual(self.image.Size, (23, 11))


  def testResizeWhileSet(self):
    """Checks if the size function behaves properly on images already allocated"""
    self.image.Size = (23,11)
    self.assertEqual(self.image.Size, (23, 11))
    self.image.AllocateImage()
    self.assertRaises(exceptions.RuntimeError, self.image.SetSize, (100,150))
    self.image.FreeImage()
    self.image.SetSize((100,150))
    self.assertEqual(self.image.Size, (100,150))
  
  def testColorSpace(self):
    """Checks color space related functions"""
    u = YAC.colorspace()
    u.major = YAC.cs_hls
  
    self.assertEqual(self.image.ColorSpace, YAC.colorspace())
    self.image.ColorSpace = u
    self.assertEqual(self.image.ColorSpace.major, YAC.cs_hls)
    self.assertEqual(self.image.ColorSpace, u)

class ImagePixelTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    pass
    
  def testPixel(self):
    self.image.SetSize((10,10))
    self.assertEqual(self.image.GetSize(), (10, 10))
    self.assertRaises(exceptions.RuntimeError, self.image.pixel, (0,10)) # should raise an error since the image is not allocated
    self.image.AllocateImage()

    p = self.image.pixel((0, 9))
    p.value = 0
    self.assertEqual(p.value, 0)
    
    del self.image
    #self.image = None
    b = True
    try:
      p.value = 10
    except Exception, e:
      b = False

    self.assertTrue(b, "it seems that the pixel's lifetime is not correctly bound to the image's lifetime")



class ImageIteratorTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    pass
    
  def testIterator(self):
    """Test iterators on images"""
    self.image.SetSize((10,10))
    self.assertEqual(self.image.GetSize(), (10, 10))
    
    self.image.AllocateImage()

    c = 0
    it = self.image.pixels
    while True:
      self.failUnless(c < (self.image.Size[0] * self.image.Size[1] + 10), 'the iterator does not seem to stop')
      
      try:
        # assign value to pixel
        it.value = c
        
        # iterates
        v = it.next()
        
        self.assertEqual(v, c, 'error on the pixel\' value : ' + str(v) + ' != ' + str(c))
      except StopIteration, e:
        # expected exception 
        break
      except Exception, e:
        print 'Caught exception', e
        break

      c += 1
      
    # number of pixels "iterated"
    self.assertEqual(c, self.image.Size[0] * self.image.Size[1])

  def testLifetime(self):
    self.image.SetSize((10,10))
    self.assert_(self.image.GetSize() == (10, 10), 'error on set size' + str(self.image.GetSize()) + " != " + str((10, 10)))
    
    self.image.AllocateImage()
    it = self.image.pixels

    self.image = None
    print it.value # if crash, then lifetimes not properly bound
    
    
  def testLifetimeFree(self):
    self.image.SetSize((10,10))
    self.assertEqual(self.image.GetSize(), (10, 10))
    
    self.image.AllocateImage()
    it = self.image.pixels

    print 0
    self.image.FreeImage()
    for i in it:
      print i
    #print it.value # should crash
    
class ImageSliceTestCase(unittest.TestCase):
  """Tests around the slice support of images"""
  def setup(self):
    pass

  def testSliceLen(self):
    """Test the slicing functionality of the image class"""
    
    im1 = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)
    size = (40, 30)
    im1.SetSize(size)
    im1.AllocateImage()

    self.assertEqual(len(im1.slice[:]), 40 * 30)

  def testSliceContent(self):
    """Test the slicing functionality of the image class"""
    
    im1 = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)
    size = (40, 30)
    im1.SetSize(size)
    im1.AllocateImage()

    im1.slice[:] = 0
    self.assertEqual(sum(im1.slice[:]), 0)

    im1.slice[:] = 2
    self.assertEqual(sum(im1.slice[:]), 2*YAI.total_number_of_points(im1))
    
    im1.slice[-3:] = 1
    self.assertEqual(sum(im1.slice[:]), 2*(YAI.total_number_of_points(im1) - 3) + 3)
    

class UtilitiesTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)
    self.image.Size = (23,11)
  def tearDown(self):
    pass

  def testTotalNumberOfPoints(self):
    self.assertEqual(YAI.total_number_of_points(self.image), 23*11)

  def testOffsetToCoordinate(self):
    c = YAI.FromOffsetToCoordinate(self.image.Size, 0)
    self.assertEqual(c, (0,0))


def suite():
  l = []
  for i in [ImageTestCase, ImagePixelTestCase, ImageIteratorTestCase, ImageSliceTestCase, UtilitiesTestCase]:
    suite = unittest.TestLoader().loadTestsFromTestCase(i)
    l.append(suite)

  return unittest.TestSuite(l)
  
if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
