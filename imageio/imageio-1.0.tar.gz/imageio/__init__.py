# -*- coding: utf-8 -*-
# Copyright (c) 2014, imageio contributors
# imageio is distributed under the terms of the (new) BSD License.

# This docstring is used at the index of the documentation pages, and
# gets inserted into a slightly larger description (in setup.py) for
# the page on Pypi:
""" 
Imageio is a Python library that provides an easy interface to read and
write a wide range of image data, including animated images, volumetric
data, and scientific formats. It is cross-platform, runs on Python 2.x
and 3.x, and is easy to install.

Main website: http://imageio.github.io
"""

__version__ = '1.0' 

# Load some bits from core
from .core import FormatManager, RETURN_BYTES  # noqa

# Instantiate format manager
formats = FormatManager()

# Load the functions
from .core.functions import help  # noqa
from .core.functions import read, imread, mimread, volread, mvolread  # noqa
from .core.functions import save, imsave, mimsave, volsave, mvolsave  # noqa

# Load all the plugins
from . import plugins  # noqa

# Clean up some names
del FormatManager
