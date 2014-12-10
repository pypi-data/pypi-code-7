#!/usr/bin/env python
from setuptools import setup

version = '0.0.1'

setup(
  name='foursquare.pants.changed',
  author='Foursquare',
  author_email='pants@foursquare.com',
  description='List, build or test locally changed targets',
  url = 'https://github.com/foursquare/pants-changed',
  version=version,
  download_url='https://github.com/foursquare/pants-changed/tags/v'+version,
  packages=['foursquare.pants.changed'],
  namespace_packages=['foursquare', 'foursquare.pants'],
  entry_points = {
    'pantsbuild.plugin': [
      'register_goals = foursquare.pants.changed.register:register',
    ]
  },
  keywords=['pantsbuild', 'pantsbuild plugin'],
)
