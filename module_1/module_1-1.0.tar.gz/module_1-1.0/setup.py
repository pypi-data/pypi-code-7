from setuptools import setup
from distutils.core import Extension

import os

os.environ["CC"] = "g++"
os.environ["CXX"] = "g++"


from distutils.core import setup
from distutils.extension import Extension
setup(name='module_1',
      version='1.0',
      ext_modules=[Extension('module1.test', ['main.cpp'])],
      )
