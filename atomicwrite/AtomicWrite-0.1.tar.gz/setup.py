"""
setup packaging script for AtomicWrite
"""

import os

version = "0.1"
dependencies = []

# allow use of setuptools/distribute or distutils
kw = {}
try:
    from setuptools import setup
    kw['entry_points'] = """
      [console_scripts]
"""
    kw['install_requires'] = dependencies
except ImportError:
    from distutils.core import setup
    kw['requires'] = dependencies

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.txt')).read()
except IOError:
    description = ''


setup(name='AtomicWrite',
      version=version,
      description="write file contents atomically in one operation",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/AtomicWrite',
      license='MIT',
      packages=['atomic'],
      include_package_data=True,
      zip_safe=False,
      **kw
      )

