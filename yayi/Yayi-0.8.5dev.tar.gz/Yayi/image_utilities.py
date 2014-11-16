# -*- coding: UTF-8 -*-
# some useful functions


from load_libraries import YAYI

from common import *
from color_utilities import colorSplitTo3, colorComposeFrom3

def copy(im):
  """Quick copy of an image into a new one.
   
   :param im: input image
   :rtype: image
   :returns: a exact copy of the input image (same type, dimensions and content).
   
   Example::
   
     imout = copy(imin)
   
   """
  im1 = YACORE.GetSameImage(im)
  YAPIX.Copy(im, im1)
  return im1

def _copy(im, scalar_type):
  """Small helper function for copy"""
  if(im.DynamicType().s_type == scalar_type):
    return copy(im)
  im1 = YACORE.GetSameImageOf(im, YACOM.type(im.DynamicType().c_type, scalar_type))
  YAPIX.Copy(im, im1)
  return im1

def copy_to_uint8(im):
  """Quick copy of an image into a new unsigned 8 bits one"""
  return _copy(im, YACOM.s_ui8)

def copy_to_uint16(im):
  """Quick copy of an image into a new unsigned 16 bits one"""
  return _copy(im, YACOM.s_ui16)
  
def copy_to_uint32(im):
  """Quick copy of an image into a new unsigned 32 bits one"""
  return _copy(im, YACOM.s_ui32)
  
def copy_to_float(im):
  """Quick copy of an image into a new 'float' one"""
  return _copy(im, YACOM.s_float)

def copy_to_double(im):
  """Quick copy of an image into a new 'double' one"""
  return _copy(im, YACOM.s_double)

def copy_to_pixel3(im):
  """Quick copy of a scalar image into a new 3 channels' one. The scalar is duplicated on each channel."""
  if(im.DynamicType().c_type != YACOM.c_scalar):
    raise RuntimeError('Input type should be scalar')
  
  im1 = YACORE.GetSameImageOf(im, YACOM.type(YACOM.c_3, im.DynamicType().s_type))
  YAPIX.CopyComposeChannels(im, im, im, im1)
  return im1



def crop_window(im, hyperrectangle = None):
  """Crops the input image to keep the specified hyperrectangle. If ``hyperrectangle`` is None, a copy
  of the input is returned (see :func:`copy`).

  :param image im: the input image that should be cropped
  :param tuple hyperrectangle: the window from ``im`` that should be extracted.
  :returns: a cropped image
  :rtype: image

  .. note:: the ``hyperrectangle`` parameter is a pair of two coordinate elements, which are respectively the starting and ending point 
            of the rectangle.
            The ending point is not included.

  .. warning:: the input window is not checked directly in python.

  .. seealso:: :func:`copy`
  
  Example::

     im = YACORE.ImageFactory(YAYI.COM.c_scalar, 2)
     im.Size = (20, 30)
     im.AllocateImage()
     cropped_image = crop_window(im, ((10, 5), (15, 20)))

  """
  
  if(hyperrectangle is None):
    return copy(im)
  else:
    size = [0 for i in hyperrectangle[0]]
    for i in range(len(size)):
      size[i] = hyperrectangle[1][i] - hyperrectangle[0][i]
    
    im1 = YACORE.ImageFactory(im.DynamicType(), im.GetDimension())
    im1.Size = size
    im1.AllocateImage()
    YAPIX.CopyWindow(im, (hyperrectangle[0], tuple(size)), ((0,0), tuple(size)), im1)
  return im1




def get_black_image(original_im):
  """Creates a scalar black image of the same geometry than the input image.

  .. note:: this function is mainly intended for drawing
  """
  out = YACORE.GetSameImageOf(original_im, YACOM.type(YACOM.c_scalar, YACOM.s_ui8))
  YAYI.PIX.Constant(0, out)
  return out



def randomize(im, excluded_value = []):
  """Assigns to each pixel value of the input image one randomly chosen color image. This function is useful for viewing 
  label images for instance.

  :param image im: input image
  :param list excluded_value: a list of values that should remain unchanged
  :returns: the input image with randomized colors
  :rtype: image

  .. note:: the input image format should be scalar integer (float/double images are not supported)

  """
  if(im.DynamicType().c_type == YACOM.c_scalar):
    if(im.DynamicType().s_type == YACOM.s_float or im.DynamicType().s_type == YACOM.s_double):
      raise UserWarning, "Randomize : can't perform randomization of colors in a Float image, returning original"
      return im
    
    elif(im.DynamicType().s_type in [YACOM.s_ui8, YACOM.s_ui16, YACOM.s_ui32]):
      hist = YAYI.MEAS.MeasHistogram(im)
      im1 = YACORE.GetSameImageOf(im, type_c3_ui8)
      #keys = [i[0] for i in hist]
      listOfColor = [(i[0], (randint(0,255), randint(0,255),randint(0,255))) for i in hist if i[0] not in excluded_value]# * (max(keys) + 1)
      #for i in keys:
      #  listOfColor[i] = (randint(0,255), randint(0,255),randint(0,255))
      #listOfColor.reverse() ## attention temporairement
      YAYI.PIX.LookupTransform(im, listOfColor, (0,0,0), im1)
      return im1















def AAbsSub(im1, im2):
  """Returns the absolute difference of the two input images
  
  .. math:: 
  
    \\forall p \\in \\mathcal{D}(im_1) \\cap \\mathcal{D}(im_2), im_o(p) = \\left|im_1(p) - im_2(p)\\right|
  
  
  """
  imtemp = YAYI.CORE.GetSameImage(im1)
  YAYI.PIX.AbsSubtract(im1, im2, imtemp)
  return imtemp

def ASub(im1, im2):
  """Returns the difference of the two images
  
  .. math:: 
    
    \\forall p \\in \\mathcal{D}(im_1) \\cap \\mathcal{D}(im_2), im_o(p) = im_1(p) - im_2(p)
    
  .. warning:: 
  
    The underflow is not checked with this function. Consider :func:`ASubClip` instead.
    
  .. seealso::
  
    :func:`ASubClip`
  
  """
  imtemp = YAYI.CORE.GetSameImage(im1)
  YAYI.PIX.Subtract(im1, im2, imtemp)
  return imtemp


def ASubClip(im1, im2, clip = 0):
  """Returns the bounded difference of the two input images
  
  .. math::
  
    \\forall p \\in \\mathcal{D}(im_1) \\cap \\mathcal{D}(im_2), im_o(p) = (im_1(p) - im_2(p)) \\vee clip
  
  """
  
  imtemp = YAYI.CORE.GetSameImage(im1)
  YAYI.PIX.SubtractLowerBound(im1, im2, clip, imtemp)
  return imtemp


def AInvert(im_i):
  """Returns the bitwise complement of the input image
  
  .. math:: 
  
    \\forall p \\in \\mathcal{D}(im_i), im_o(p) = \\sim im_i(p)
  
  """
  imtemp = YAYI.CORE.GetSameImage(im_i)
  YAYI.PIX.BitwiseNot(im_i, imtemp)
  return imtemp

def AOr(im1, im2):
  """Returns the bitwise union (or) of the two input images
  
  .. math::
  
    \\forall p \\in \\mathcal{D}(im_1) \\cap \\mathcal{D}(im_2), im_o(p) = im_1(p)\\  |\\  im_2(p)
  
  """
  if(im1.DynamicType().c_type == c_3 and im2.DynamicType().c_type == c_scalar):
    u1, u2, u3 = colorSplitTo3(im1)
    imtemp = colorComposeFrom3(AOr(u1, im2), AOr(u2, im2), AOr(u3, im2))
  elif(im2.DynamicType().c_type == c_3 and im1.DynamicType().c_type == c_scalar):
    u1, u2, u3 = colorSplitTo3(im2)
    imtemp = colorComposeFrom3(AOr(u1, im1), AOr(u2, im1), AOr(u3, im1))
  elif(im2.DynamicType().c_type == c_3 and im1.DynamicType().c_type == c_3):
    u1, u2, u3 = colorSplitTo3(im1)
    z1, z2, z3 = colorSplitTo3(im2)
    imtemp = colorComposeFrom3(AOr(u1, z1), AOr(u2, z2), AOr(u3, z3))
  else:
    imtemp = YAYI.CORE.GetSameImage(im1)
    YAYI.PIX.BitwiseOr(im1, im2, imtemp)
  return imtemp

