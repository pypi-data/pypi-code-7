# -*- coding: UTF-8 -*-
# Morphological functions


from . import YAYI
from . import image_utilities as UT
from .common import *

def MSup(im1, im2):
  """Computes the supremum (value union) of two images.
  
  .. math:: 
    \\forall p \\in \\mathcal{D}(im_1) \\cap \\mathcal{D}(im_2), im_o(p) = im_1(p) \\vee im_2(p)
    
  """
  imout = YAYI.CORE.GetSameImage(im1)
  YAYI.PIX.Union(im1, im2, imout)
  return imout

def MInf(im1, im2):
  """Computes the infimum (value intersection) of two images
  
  .. math:: 
    \\forall p \\in \\mathcal{D}(im_1) \\cap \\mathcal{D}(im_2), im_o(p) = im_1(p) \\wedge im_2(p)
  
  """
  imout = YAYI.CORE.GetSameImage(im1)
  YAYI.PIX.Intersection(im1, im2, imout)
  return imout



def MDilate(im, size = 1, se = hex2D):
  """Dilates ``im`` with the structuring element ``se``.
  
  :param image im: input image to dilate
  :param integer size: the size of the dilation. 
  :param structuring-element se: the structuring element used for the dilation.
  
  .. note::
     This operation is homothetic if ``size`` > 1.
  """
  if(size > 1):
    imout = YAYI.CORE.GetSameImage(im)
    imtemp= YAYI.CORE.GetSameImage(im)
    YAYI.LMM.Dilation(im, se, imtemp)
    for i in range(1, size):
      YAYI.LMM.Dilation(imtemp, se, imout)
      imtemp, imout = imout, imtemp
  elif (size == 0):
    return im
  else:
    imout = YAYI.CORE.GetSameImage(im)
    YAYI.LMM.Dilation(im, se,imout)
  return imout


def MErode(im, size = 1, se = hex2D):
  """Erodes ``im`` with the structuring element ``se``. 
  
  
  .. note::
     This operation is homothetic if ``size`` > 1.
  
  """
  if(size > 1):
    imout = YAYI.CORE.GetSameImage(im)
    imtemp= YAYI.CORE.GetSameImage(im)
    YAYI.LMM.Erosion(im, se, imtemp)
    for i in range(1, size):
      YAYI.LMM.Erosion(imtemp, se, imout)
      imtemp, imout = imout, imtemp
  elif (size == 0):
    return im
  else:
    imout = YAYI.CORE.GetSameImage(im)
    YAYI.LMM.Erosion(im, se,imout)
  return imout


def MClose(im, size = 1, se = hex2D):
  """Closes of the input image with se as structuring element. Homothetic dilation/erosion is used if size > 1."""

  if(size > 1):
    imout = MDilate(im, size, se)
    return MErode(imout, size, se)
  elif (size == 0):
    return im
  else:
    imout = YAYI.CORE.GetSameImage(im)
    YAYI.LMM.Close(im, se, imout)
  return imout

def MOpen(im, size = 1, se = hex2D):
  """Opens of the input image with se as structuring element. Homothetic dilation/erosion is used if size > 1."""

  if(size > 1):
    imout = MErode(im, size, se)
    return MDilate(imout, size, se)
  elif (size == 0):
    return im
  else:
    imout = YAYI.CORE.GetSameImage(im)
    YAYI.LMM.Open(im, se, imout)
  return imout


def MWatershed(imIn, nl = hex2D):
  """Thick version of the watershed"""
  imOut   = YAYI.CORE.GetSameImageOf(imIn, Ytype(c_scalar, sUI16))
  YAYI.SEG.IsotropicWatershed(imIn, nl, imOut)
  return imOut


def MWatershedCons(imIn, mk, nl = hex2D):
  """Thick version of the constrained watershed"""
  imOut = YAYI.CORE.GetSameImage(mk)
  YAYI.SEG.IsotropicSeededWatershed(imIn, mk, nl, imOut)
  return imOut