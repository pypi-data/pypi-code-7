#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
This package is written as part of ROSA Linux repository testing tools.
The licence of this package is GNU GPL v3.

Authors of this package:
Egor.Kochetoff@gmail.com
myxomopla@gmail.com
maria.mamontova1993@gmail.com
iknizhnikova@gmail.com

@package repochecker_binsym
This package checks that rpm repository is closed in terms of binary symbols,
i.e. every binary symbol requested by every binary in the repository
is provided by some package from the repository
'''

import yaml
import os

config = None
broken_packages = []
errors = {}

def init (cfg):
  global config
  config = cfg
  if not os.path.isdir(config ['log']):
    os.mkdir (config ['log'])

def log_package_details (package, details):
  fname = os.path.join(config ['log'], package)
  file (fname, 'w').write(yaml.safe_dump({'unsatisfied symbols' : tuple (details)}))
  broken_packages.append(package)

def error (package, msg):
  if package not in errors:
    errors [package] = [msg]
  else:
    errors [package].append(msg)

def commit():
  fname = os.path.join(config ['log'], 'summary.yaml')
  data = {'broken': tuple (broken_packages),
          'errors': errors
         }
  file (fname, 'w').write(yaml.safe_dump(data))

#*** READY ***
#Analysis took 0:18:28.649172 76.41%
#Dependency calculation took 0:00:56.688084 3.86%
#DB write took 0:04:44.751100 19.59%

#Overall working time: 0:24:10.088356

#*** READY ***
#Analysis took 0:00:15.531231 0.59%
#Dependency calculation took 0:38:17.069464 89.59%
#DB write took 0:04:11.592986 9.79%

#Overall working time: 0:42:44.193681
