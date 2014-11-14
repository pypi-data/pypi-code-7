# -*- coding: UTF-8 -*-
# Raffi Enficiaud
# This file contains utilities for color processing

from common import *

def colorSplitTo3(im):
  """Splits the input 3-channel image into 3 outputs, each of them corresponding to one of the input's channel"""
  if(im.DynamicType().c_type != c_3):
    raise 'Only color image'
  im1 = YAYI.CORE.GetSameImageOf(im, Ytype(c_scalar, im.DynamicType().s_type))
  im2 = YAYI.CORE.GetSameImage(im1)
  im3 = YAYI.CORE.GetSameImage(im1)
  YAYI.PIX.CopySplitChannels(im, im1, im2, im3)
  return im1, im2, im3
  
def colorGetChannel(im, channel):
  """Returns a copy of the specified channel.
   
   :param image im: input image
   :param int channel: the desired channel
   :rtype: image
   :returns: copy of the specified channel of the input image
   
   Example::
   
     imout = colorGetChannel(imin, 2)
   
  
  """
  if(im.DynamicType().c_type != c_3):
    raise 'Only color image'
  im1 = YAYI.CORE.GetSameImageOf(im, Ytype(c_scalar, im.DynamicType().s_type))
  YAYI.PIX.CopyOneChannel(im, channel, im1)
  return im1

def colorComposeFrom3(im1, im2, im3):
  """Combines the 3 mono-channel images into one 3-channels image"""
  im = YAYI.CORE.GetSameImageOf(im1, Ytype(c_3, im1.DynamicType().s_type))
  YAYI.PIX.CopyComposeChannels(im1, im2, im3, im)
  return im







def HLS1FromRGB(im):
  """Transforms the input RGB UInt8 image into the HLS (hue, luma, saturation) color space. The definition of the HUE used
  is the one using the l1 norm (see Hanbury). 
  
   :param im: input RGB image 
   :rtype: image
   :returns: same image, in the HLS color space. The hue, luma and saturation channels are in this order
  
  """
  imhls = YAYI.CORE.GetSameImageOf(im, Ytype(c_3, sFl))
  YAYI.PIX.color_RGB_to_HLS_l1(im, imhls)
  return imhls


def ThresholdCircularDomainDegres(im, angle_in, angle_out):
  """Returns a binary image corresponding to a threshold of the input image expressed in an angular domain. This is basically 
  a threshold function, except the fact that it handles correctly the case angle_in > angle_out of the circular domain.
  
  If angle_in < angle_out, we have:
  
  .. math:: 
    \\forall p \\in \\mathcal{D}(im), im_o(p) = \\left\\{\\begin{array}{ll}255&im_1(p) \\in [a_{in}, a_{out}[\\\\ 0 & otherwise\\end{array}\\right.
  
  If angle_in > angle_out, we have

  .. math:: 
    \\forall p \\in \\mathcal{D}(im), im_o(p) = \\left\\{\\begin{array}{ll}255&im_1(p) \\in [a_{in}, 360[ \\cup [0, a_{out}[\\\\ 0 & otherwise\\end{array}\\right.

  
  :param im: the input image to be thresholded (should be mono-channel)
  :param angle_in: the beginning of the interval (integer)
  :param angle_out: the end of the interval (integer)
  :rtype: a "binary" mask image, where 255 indicates the points in the desired interval (0 otherwise) 
   """
   
  imout = YAYI.CORE.GetSameImageOf(im, Ytype(c_scalar, sUI8))

  angle_in = angle_in % 360
  angle_out= angle_out % 360

  if(angle_in > angle_out):
    YAYI.PIX.Threshold(im, float(angle_in) * (m.pi / 180.0), 359.99 * (m.pi / 180.0), 255, 0, imout)
    if(angle_out > 0):
      imout2 = YAYI.CORE.GetSameImage(imout)
      YAYI.PIX.Threshold(im, 0, float(angle_out) * (m.pi / 180.0), 255, 0, imout2)
      imout = AOr(imout, imout2)
      del imout2
    
  else:
    YAYI.PIX.Threshold(im, float(angle_in) * (m.pi / 180.0), float(angle_out) * (m.pi / 180.0), 255, 0, imout)
    
  return imout

