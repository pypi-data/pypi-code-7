#!/usr/bin/env python

# 
# Copyright (C) 2010-2012 Platform Computing
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
# 
import os
from distutils.core import setup, Extension

# http://sourceforge.net/mailarchive/message.php?msg_id=28474701
# hack distutils so that extensions are built before python modules;
# this is necessary for SWIG-generated .py files
from distutils.command.build import build
build.sub_commands = [('build_ext', build.has_ext_modules),
                     ('build_py', build.has_pure_modules),
                     ('build_clib', build.has_c_libraries),
                     ('build_scripts', build.has_scripts)]

lsf_include_dir = os.getenv('LSF_INCLUDEDIR')
if not lsf_include_dir:
      raise Exception('LSF_INCLUDEDIR not found in environment variables')
lsf_library_dir = os.getenv('LSF_LIBDIR')
if not lsf_library_dir:
      raise Exception('LSF_LIBDIR not found in environment variables')

setup(name='platform-python-lsf-api',
      version='0.0.3',
      description='Python binding for Platform LSF APIs',
      license='LGPL',
      keywords='LSF,Grid,Cluster,HPC',
      url='http://www.platform.com',
      py_modules=['pythonlsf.lsf'],
      ext_package='pythonlsf',
      ext_modules=[Extension('_lsf', ['pythonlsf/lsf.i'],
                               swig_opts=['-I%s' % (lsf_include_dir)],
                               include_dirs=[lsf_include_dir],
                               library_dirs=[lsf_library_dir],
                               libraries=['c', 'nsl', 'lsf', 'bat',
                                            'fairshareadjust', 'lsbstream'])],
      classifiers=["Development Status :: 2 - Pre-Alpha",
                     "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                     "Operating System :: OS Independent",
                     "Programming Language :: Python",
                     "Topic :: Internet",
                     "Topic :: Scientific/Engineering",
                     "Topic :: Software Development",
                     "Topic :: System :: Distributed Computing",
                     "Topic :: Utilities",
                     ],
     author='Platform Computing',
     maintainer='Mark Burnett',
     maintainer_email='mburnett@genome.wustl.edu',
     )

