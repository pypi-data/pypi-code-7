#!/usr/bin/env python

from setuptools import setup, find_packages
from wekit import VERSION

url="https://coding.net/u/jeff/p/wekit/git"

long_description="Weteam Python SDK"

setup(name="wekit",
      version=VERSION,
      description=long_description,
      maintainer="jeff kit",
      maintainer_email="bbmyth@gmail.com",
      url = url,
      long_description=long_description,
      packages=find_packages('.'),
     )


