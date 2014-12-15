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

import time
import datetime

config = None

def init (cfg):
  global config
  config = cfg
  ldir = config ['log']
  if not os.path.isdir(ldir):
    os.mkdir (ldir)
  fname = os.path.join(ldir, 'errors.yaml')
  if os.path.exists(fname):
    os.remove(fname)
  fname = os.path.join(ldir, 'broken.yaml')
  if os.path.exists(fname):
    os.remove(fname)

  fname = os.path.join(ldir, 'last-check.yaml')
  with open(fname, 'w') as f:
    f.write (datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S\n'))

def log_package_details (package, details):
  fname = os.path.join(config ['log'], 'broken.yaml')
  data = { package : details }
  with open(fname, 'a') as outfile:
    outfile.write (yaml.dump(data))

def error (package, msg):
  fname = os.path.join(config ['log'], 'errors.yaml')
  data = { package : msg }
  with open(fname, 'a') as outfile:
    outfile.write (yaml.dump(data))
