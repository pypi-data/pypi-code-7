#
#   Copyright (c) 2014, Scott J Maddox
#
#   This file is part of SimpleQW.
#
#   SimpleQW is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   SimpleQW is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with SimpleQW.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

# std lib imports
from setuptools import setup
import os

# read in __version__
exec(open('src/simpleqw/version.py').read())

# Prepare cython. This pattern performs a late import of Cython,
# so that setuptools/pip has a chance to install them first.
# class LazyList(list):
#     def __init__(self, func):
#         self.__func = func
#         self.__initialized = False
#         self.__list = None
#     
#     def __getattr__(self, attr):
#         if not self.__initialized:
#             self.__list = self.__func()
#             self.__initialized = True
#         return getattr(self._list, attr)
#  
# def get_extensions():
#     from Cython.Build import cythonize
#     cython_modules = ['src/simpleqw/finite_well_1d.pyx']
#     return cythonize(cython_modules)

from Cython.Build import cythonize
cython_modules = ['src/simpleqw/finite_well_1d.pyx']
ext_modules = cythonize(cython_modules)


setup(
    name='SimpleQW',
    version=__version__,  # read from version.py
    description='simple quantum well computations',
    long_description=open('README.rst').read(),
    url='http://scott-maddox.github.io/simpleqw',
    author='Scott J. Maddox',
    author_email='smaddox@utexas.edu',
    license='AGPLv3',
    packages=['simpleqw',
              'simpleqw.tests',],
    package_dir={'simpleqw': 'src/simpleqw'},
    setup_requires=['cython>=0.17'],
    install_requires=['cython>=0.17'],
    tests_require=['cython>=0.17'],
    test_suite = 'simpleqw.tests',
    zip_safe=True,
#     ext_modules=LazyList(get_extensions),
    ext_modules=ext_modules,
)