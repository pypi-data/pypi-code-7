#!/usr/bin/env python

from setuptools import setup
from apnsagent import VERSION

long_description="python SDK for apnsagent http://apns.sutui.me"

setup(name="apnsclient",
      version=VERSION,
      description="APNSagent Python client",
      maintainer="jeff kit",
      maintainer_email="bbmyth@gmail.com",
      url = '',
      long_description=long_description,
      scripts = [],
      packages=['apnsagent'],
      package_data={'apnsagent': []},
     )
