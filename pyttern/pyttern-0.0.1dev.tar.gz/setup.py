from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='pyttern',
      version='0.0.1',
      description='common pattern for python',
      long_description='common pattern for python',
      classifiers=[],# Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords=['pattern', 'fsm'],
      author='yangtianhang',
      author_email='tianhang.yang@gmail.com',
      url='https://github.com/yangtianhang/pyttern',
      download_url='https://github.com/yangtianhang/pyttern/tarball/0.0.1',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      )
