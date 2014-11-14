# -*- coding: UTF-8 -*-

from load_libraries import YAYI

YACOM   = YAYI.COM
YACORE  = YAYI.CORE
YAPIX   = YAYI.PIX
YAMEAS  = YAYI.MEAS
YAIO    = YAYI.IO
YAREC   = YAYI.REC

type_scalar_ui8   = YACOM.type(YACOM.c_scalar, YACOM.s_ui8)
type_scalar_ui16  = YACOM.type(YACOM.c_scalar, YACOM.s_ui16)
type_c3_ui8       = YACOM.type(YACOM.c_3, YACOM.s_ui8)
Ytype             = YACOM.type

c_scalar  = YAYI.COM.c_scalar
c_3       = YAYI.COM.c_3
c_complex = YAYI.COM.c_complex
sUI8      = YAYI.COM.s_ui8
sI8       = YAYI.COM.s_i8
sUI16     = YAYI.COM.s_ui16
sI16      = YAYI.COM.s_i16
sFl       = YAYI.COM.s_float
sDl       = YAYI.COM.s_double

e_Candidate ,e_Done, e_Queued, e_Queued2, e_Watershed = (0,1,2,3,4)

c_scalar  = YAYI.COM.c_scalar
c_3       = YAYI.COM.c_3
c_complex = YAYI.COM.c_complex
sUI8      = YAYI.COM.s_ui8
sI8       = YAYI.COM.s_i8
sUI16     = YAYI.COM.s_ui16
sI16      = YAYI.COM.s_i16
sFl       = YAYI.COM.s_float
sDl       = YAYI.COM.s_double

Ytype     = YAYI.COM.type

hex2D     = YAYI.SE.SEHex2D()
hex2D.__doc__ = "Hexagonal 2D structuring element"
hex2D_nc  = YAYI.SE.SEHex2D()

sq2D      = YAYI.SE.SESquare2D()
#sq2D_nc   = YAYI.SE.SESquare2D()

cross2D   = YAYI.SE.SECross2D()
#cross2D_nc= cross2D

comparison_operations = YAYI.PIX.comparison_operations


def deprecated(func):
  """This is a decorator which can be used to mark functions as deprecated. It will result in a warning being emitted when the function is used."""
  def newFunc(*args, **kwargs):
      warnings.warn("Call to deprecated function %s." % func.__name__, category=DeprecationWarning)
      return func(*args, **kwargs)
  newFunc.__name__ = func.__name__
  newFunc.__doc__ = func.__doc__
  newFunc.__dict__.update(func.__dict__)
  return newFunc

