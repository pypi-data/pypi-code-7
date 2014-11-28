#!/usr/bin/env python
# -*- coding: utf8 -*-
from setuptools import setup

setup(name='tardocken',
      description='Add extra context to docker builds.',
      maintainer='Kit Barnes',
      maintainer_email='kit@ninjalith.com',
      url='https://github.com/KitB/tardocken',
      version='0.1',
      packages=['tardocken'],
      zip_safe=True,
      scripts=['bin/tardocken'],
      keywords=['docker'],
      )
