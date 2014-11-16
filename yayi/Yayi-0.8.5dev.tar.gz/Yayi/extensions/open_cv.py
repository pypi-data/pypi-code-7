# -*- coding: UTF-8 -*-

# test for transforming an yayi image to an opencv compatible image

from Yayi.load_libraries import YAYI

import cv


map_scalar_data_t_to_open_cv = {YAYI.COM.s_ui8:     cv.IPL_DEPTH_8U, 
                                YAYI.COM.s_i8:      cv.IPL_DEPTH_8S, 
                                YAYI.COM.s_ui16:    cv.IPL_DEPTH_16U, 
                                YAYI.COM.s_i16:     cv.IPL_DEPTH_16S,
                                YAYI.COM.s_ui32:    cv.IPL_DEPTH_32U, 
                                YAYI.COM.s_i32:     cv.IPL_DEPTH_32S,
                                YAYI.COM.s_float:   cv.IPL_DEPTH_32F, 
                                YAYI.COM.s_double:  cv.IPL_DEPTH_64F}

 
map_data_type_to_nb_channels = {YAYI.COM.c_scalar: 1, YAYI.COM.c_3: 3, YAYI.COM.c_4:4, YAYI.COM.c_complex:2}

def yayi_to_opencv(im1):
  """Transforms an Yayi image into an OpenCV image. The intermediate numpy array does not involve a copy.
  >>> imyayi = YAYI.IO.readJPG(os.path.join(os.path.dirname(__file__), os.pardir, "data", "test.jpg"))
  >>> imopencv = yayi_to_opencv(imyayi)
  
  """
  nmim = YAYI.IO.image_to_numpy(im1)
  nb_channels = map_data_type_to_nb_channels[im1.DynamicType().c_type]
  cv_im = cv.CreateImageHeader(tuple([int(i) for i in im1.Size]),
                               map_scalar_data_t_to_open_cv[im1.DynamicType().s_type],
                               nb_channels)
  
  # it seems to me that tostring involves a copy
  cv.SetData(cv_im, nmim.tostring(), nmim.dtype.itemsize * nb_channels * nmim.shape[1])
  return cv_im


if __name__ == "__main__":
  import doctest
  doctest.testmod()