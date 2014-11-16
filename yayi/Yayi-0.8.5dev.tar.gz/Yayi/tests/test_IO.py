#!/usr/bin/python
# -*- coding: utf8 -*-
# author: Raffi Enficiaud

# set YAYIPATH=P:\Perso\Tmp\YAYI_SVN1320\Release
# set PATH=P:\Perso\externals\lib\;%PATH%
# python -m unittest -v test_image_utilities.py

import os, sys, types, inspect
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import Yayi.image_utilities as UTILS
YAYI = UTILS.YAYI

try:
  import numpy
  has_numpy = True
except Exception, e:
  has_numpy = False


class test_IO(unittest.TestCase):

  def setUp(self):
    self.path_images = os.path.join(os.path.dirname(__file__), 
                                     os.pardir, os.pardir, os.pardir, os.pardir, 
                                     "coreTests", "yayiTestData")

  def test_tiff(self):
    pass