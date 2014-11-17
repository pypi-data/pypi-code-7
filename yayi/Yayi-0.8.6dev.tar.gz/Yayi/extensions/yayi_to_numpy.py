# -*- coding: UTF-8 -*-

__doc__ = """Utilities for binding yayi and numpy"""

from .. import YAYI



def yayi_to_numpy(im1):
  """Transforms an Yayi image into an OpenCV image. The intermediate numpy array does not involve a copy.
  >>> imyayi = YAYI.IO.readJPG(os.path.join(os.path.dirname(__file__), os.pardir, "data", "test.jpg"))
  >>> numpy_img = yayi_to_numpy(imyayi)
  
  """
  nmim = YAYI.IO.image_to_numpy(im1)
  return nmim


if __name__ == "__main__":
  import doctest
  doctest.testmod()