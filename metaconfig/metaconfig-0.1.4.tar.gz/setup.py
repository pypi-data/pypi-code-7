# BSD Licence
# Copyright (c) 2010, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

from setuptools import setup, find_packages
import sys, os

__version__ = '0.1.4'
__description__ = """

Metaconfig
==========

Metaconfig is a library for centralising your Python's ConfigParser
files.  It is inspired by the logging module where it is increadibly
easy to start writing code that depends on logging whilst deferring
how log messages will be handled until later.

To get started with metaconfig just do::

  import metaconfig
  conf = metaconfig.get_config(__name__)

conf will be a ConfigParser instance.  You can create a centralised
config file to configure multiple applications and libraries.

Further documentation is available at http://packages.python.org/metaconfig/.

"""

setup(name='metaconfig',
      version=__version__,
      description="A ConfigParser bootstraping library",
      long_description=__description__,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries',
        ], 
      keywords='',
      author='Stephen Pascoe',
      author_email='Stephen.Pascoe@stfc.ac.uk',
      url='',
      download_url='http://ndg.nerc.ac.uk/dist',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points= """
        [paste.filter_factory]
        main = metaconfig.wsgi:filter_factory
        """,
      test_suite='nose.collector',
      )
