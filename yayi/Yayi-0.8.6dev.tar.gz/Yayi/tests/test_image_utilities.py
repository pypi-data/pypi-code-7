#!/usr/bin/python
# -*- coding: utf8 -*-
# author: Raffi Enficiaud

# set YAYIPATH=P:\Perso\Tmp\YAYI_SVN1320\Release
# set PATH=P:\Perso\externals\lib\;%PATH%
# python -m unittest -v test_image_utilities.py

import os, sys, types, inspect
import unittest
from Yayi import YAYI


class test_image_utilities(unittest.TestCase):

  def setUp(self):
    self.path_images = os.path.join(os.path.dirname(__file__), 
                                     os.pardir, os.pardir, os.pardir, os.pardir, 
                                     "coreTests", "yayiTestData")
    
  def test_unary_functions_are_working(self):
    """Tests unary functions of the image_utilities module"""
    im_test = YAYI.IO.readJPG(os.path.join(self.path_images, "release-grosse bouche.jpg"))
    source_utils = os.path.normpath(os.path.abspath(inspect.getsourcefile(UTILS)))
    
    
    for name, ff in inspect.getmembers(UTILS):
      if(not inspect.isfunction(ff)):
        continue
      
      if(name[0] == '_'): continue
      
      argspec = inspect.getargspec(ff)
      if(len(argspec[0]) != 1):
        continue
      
      source_function = os.path.normpath(os.path.abspath(inspect.getsourcefile(ff))) 
      if(source_function != source_utils):
        print 'function', name, 'defined in', source_function, ' --> ', 'skipping'
        continue
      
      try:
        self.assertIsNotNone(ff.__call__(im_test), "returned image does not seem to be valid for function " + str(name))
      except RuntimeError, e:
        print "runtime error '%s'" % e, 'raised in function', name
        pass

  def test_binary_functions_are_working(self):
    """Tests binary functions of the image_utilities module"""
    im_test = YAYI.IO.readJPG(os.path.join(self.path_images, "release-grosse bouche.jpg"))
    source_utils = os.path.normpath(os.path.abspath(inspect.getsourcefile(UTILS)))
    
    
    for name, ff in inspect.getmembers(UTILS):
      if(not inspect.isfunction(ff)):
        continue
      
      if(name[0] == '_'): continue
      
      argspec = inspect.getargspec(ff)
      if(len(argspec[0]) != 2):
        continue
      
      source_function = os.path.normpath(os.path.abspath(inspect.getsourcefile(ff))) 
      if(source_function != source_utils):
        print 'function', name, 'defined in', source_function, ' --> ', 'skipping'
        continue
      
      try:
        self.assertIsNotNone(ff.__call__(im_test, im_test), "returned image does not seem to be valid for function " + str(name))
      except RuntimeError, e:
        print "runtime error '%s'" % e, 'raised in function', name
        pass
