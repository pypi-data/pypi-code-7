#!/usr/bin/env python
from setuptools import setup

version = '0.0.1'

setup(
  name='foursquare.pants.rules',
  author='Foursquare',
  author_email='pants@foursquare.com',
  description='BUILD graph validate rules plugin for pants build',
  url = 'https://github.com/foursquare/pants-rules',
  version=version,
  download_url='https://github.com/foursquare/pants-rules/tags/v'+version,
  packages=['foursquare.pants.rules'],
  namespace_packages=['foursquare', 'foursquare.pants'],
  entry_points = {
    'pantsbuild.plugin': [
      'register_goals = foursquare.pants.rules.register:register',
    ]
  },
  keywords=['pantsbuild', 'pantsbuild plugin', 'BUILD graph'],
)
