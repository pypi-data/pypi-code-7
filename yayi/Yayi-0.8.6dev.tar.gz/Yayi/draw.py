# -*- coding: UTF-8 -*-


from . import YAYI
from .image_utilities import *


__doc__ = """
This module contains a lot of drawing utilities using Yayi. These are basic implementation on what is not really supported on the C++ level.

"""



def _trunc(v):
  """Truncation function"""
  if(v == 0): return v
  i = m.modf(v)
  if(v > 0):
    if(i[0] < 0.5): 
      return int(i[1])
    return int(i[1]+1)
  else:
    if(i[0] > -0.5): 
      return int(i[1])
    return int(i[1]-1)


def DrawEmptyRect(im, box, colour, with_copy = True):
  """Draws an empty rectangle of colour "colour", which location and dimension is specified by the 2-2-uple box. 
  If with_copy is True, a copy of the input image is returned, otherwise the drawing occurs on the provided image. 
  colour should be compatible with the image format."""
  if(not with_copy):
    imout = im
  else:
    if(type(colour) is types.TupleType):
      if(len(colour) == 3 and im.DynamicType().c_type == YACOM.c_scalar):
        imout = copy_to_pixel3(im)
      else:
        imout = copy(im)
    else:
      imout = copy(im)
  
  (x, y), (xend, yend) = box
  for i in range(x, xend):
    imout.pixel((i, y)).value = colour    
    imout.pixel((i, yend)).value = colour

  for i in range(y, yend):
    imout.pixel((x, i)).value = colour    
    imout.pixel((xend, i)).value = colour

  return imout



def DrawOffsetsList(im, list_offsets, constant = 255):
  """Draws a sequence of points in im on each point specified by the offsets in list_offsets. Note that even if im is returned,
  it is also modified.  
  """
  ccl = YAYI.CORE.FromOffsetsToCoordinates(im.Size,list_offsets)
  for i in ccl:
    im.pixel(i).value = constant
  return im

def DrawLineOriented(im, start_point, size, angle, constant = 255):
  """This function creates a segment of size "size" and with orientation "angle".
  
    :param image im: the image on which the line is drawn. This image is modified.
    :param start_point: the origin of the line
    :param size: the length of the line
    :param angle: the angle of the line, expressed in radius. The image orientation is from left to right, and from top to 
      bottom.
    :param constant: the 'color' of the line (should be of the type of the pixel, either scalar or tuple). 
    :rtype: the image with the line"""

  for i in range(size):
    p = _trunc(start_point[0] + i*m.cos(angle)), _trunc(start_point[1] + i*m.sin(angle))
    im.pixel(p).value = constant
    
  return im

def makePlateOfPictures(l, nbrows = 3):
  """Creates a plate of images contained in the list l (list of pictures). Supposes that all images are of the same size"""
  if(not(type(l) is list)):
    raise 'Only list of images accepted'
  
  nbrows = min(nbrows, len(l))
  height = int(ceil(float(len(l)) / float(nbrows)) * l[0].Size[1])
  width = l[0].Size[0] * nbrows
  im = YACORE.ImageFactory(l[0].DynamicType(), 2)
  im.Size = (width, height)
  im.AllocateImage()
  YAPIX.Constant(minValue(im), im)
  
  for i in range(len(l)):
    y,x = divmod(i, nbrows)
    win = (x*l[0].Size[0],y*l[0].Size[1]),(l[0].Size[0],l[0].Size[1])
    #print l[i], im, win
    #print ((0)*len(l[i].Size), l[i].Size)
    YAPIX.CopyWindow(l[i], ([0]*len(l[i].Size), l[i].Size), win, im)
  
  return im

def overlay(image_originale, imline, colour = (255, 0,0)):
  """overlay de imline dans l'image originale av colour"""
  if(image_originale.DynamicType().c_type == YACOM.c_3):
    out = YACORE.GetSameImage(image_originale)
    t_ui1 = YACORE.GetSameImageOf(image_originale, Ytype(YACOM.c_scalar, image_originale.DynamicType().s_type))
    t_ui2,t_ui3 = YACORE.GetSameImage(t_ui1), YACORE.GetSameImage(t_ui1)
    out = YACORE.GetSameImageOf(image_originale, Ytype(YACOM.c_3, image_originale.DynamicType().s_type))
    YAYI.PIX.CopySplitChannels(image_originale, t_ui1, t_ui2, t_ui3)

    for c,t in zip(colour, [t_ui1, t_ui2, t_ui3]):
      YAYI.PIX.CompareSI(imline, comparison_operations.op_equal, 0, t, c, t)
    YAPIX.CopyComposeChannels(t_ui1, t_ui2, t_ui3, out)

  else:
    if(len(colour) == 1):
      out = YACORE.GetSameImageOf(image_originale, Ytype(YACOM.c_scalar, image_originale.DynamicType().s_type))
      YAYI.PIX.CompareSI(imline, comparison_operations.op_equal, 0, image_originale, colour[0], out)
    else:
      t_ui1 = YACORE.GetSameImageOf(image_originale, Ytype(YACOM.c_scalar, image_originale.DynamicType().s_type))
      t_ui2,t_ui3 = YACORE.GetSameImage(t_ui1), YACORE.GetSameImage(t_ui1)
      out = YACORE.GetSameImageOf(image_originale, Ytype(YACOM.c_3, image_originale.DynamicType().s_type))
      for c,t in zip(colour, [t_ui1, t_ui2, t_ui3]):
        YAYI.PIX.CompareSI(imline, comparison_operations.op_equal, 0, image_originale, c, t)
      YAPIX.CopyComposeChannels(t_ui1, t_ui2, t_ui3, out)
  return out

