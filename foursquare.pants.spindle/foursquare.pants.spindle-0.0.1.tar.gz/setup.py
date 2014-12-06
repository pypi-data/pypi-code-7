#!/usr/bin/env python
from setuptools import setup

version = '0.0.1'

setup(
  name='foursquare.pants.spindle',
  author='Foursquare',
  author_email='pants@foursquare.com',
  description='Spindle Thrift-to-Scala code generation plugin for pants build system',
  url = 'https://github.com/foursquare/pants-spindle',
  version=version,
  download_url='https://github.com/foursquare/pants-spindle/tags/v'+version,
  packages=['foursquare.pants.spindle'],
  namespace_packages=['foursquare', 'foursquare.pants'],
  entry_points = {
    'pantsbuild.plugin': [
      'register_goals = foursquare.pants.spindle.spindle_codegen_task:register',
      'build_file_aliases = foursquare.pants.spindle.spindle_codegen_task:aliases',
    ]
  },
  keywords=['pantsbuild', 'pantsbuild plugin', 'thrift', 'scala', 'codegen'],
)
