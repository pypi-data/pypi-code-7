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

# TODO rewrite it from yaml to sqlite/sql with server — to boost efficiency
import yaml
import os

# All the variables below are for internal module use only,
# they will be changed in next releases

# dbpath stores database name
config = None
# list of previously processed packages with metadata
packages = None
# map: package -> list of required symbols
requires = None
# set of all provided symbols
provides = None
dbpath = ''

def init (cfg):
  global dbpath
  '''
  Module API function

  Specify config for further module operation.
  Config needs to be a map for one given repository
  Config contains at lease value «db» with database file path or database name
  '''
  global config
  config = cfg
  dbpath = cfg ['path']

def _load_packages():
  '''
  This is internal function that loads internal variable 'packages' from db.
  '''
  global packages
  if packages == None:
    fname = os.path.join(dbpath, 'packages')
    if os.path.isfile(fname):
      packages = yaml.load (file (fname, 'r'), Loader=yaml.loader.BaseLoader)
    if packages == None:
      packages = {}
      return False

def _load_provides():
  '''
  This is internal function that loads internal variable 'provides' from db
  '''
  global provides
  if provides == None:
    fname = os.path.join(dbpath, 'provides')
    if os.path.isfile(fname):
      provides = set (yaml.load (file (fname, 'r'), Loader=yaml.loader.BaseLoader))
    if provides == None:
      provides = set ()

def _load_requires():
  '''
  This is internal function that loads internal variable 'requires' from db
  '''
  global requires
  if requires == None:
    fname = os.path.join(dbpath, 'requires')
    if os.path.isfile(fname):
      requires = yaml.load (file (fname, 'r'), Loader=yaml.loader.BaseLoader)
    if requires == None:
      requires = {}

def is_package_analyzed (package_name, modification_time, filesize):
  '''
  Module API function

  Returns whether all relevant information about package has been cached
  package_name: string, filename of the package
  modification_time: modification time of the package file as reported by `stat`
  filesize: size of file as reported by `stat`

  If the package with given name, modification_time and filesize is found in db,
  it is consideted to be processed earlier and does not need to be examined
  '''
  global packages
  _load_packages()
  if not package_name in packages:
    return False
  package = packages [package_name]
  return int(package ['mtime']) == int(modification_time) and \
         int(package [ 'size']) == int(filesize)

def dump_package_info (package_name, modification_time, filesize, requires_list, provides_list):
  '''
  Module API function

  Stores information about the given package to db and updates cached package list.
  package_name: filename of the package
  modification_time: modification time of the package file as reported by `stat`
  filesize: size of file as reported by `stat`
  requires_list: list of binary symbols required by the package
  provides_list: list of binary symbols provided by the package

  This function should also be able to remove provided binary symbols from db
  if the package does not provide some of them anymore.
  Currently, this quick&dirty implementation does not do that.
  '''
  global packages, provides, requires
  _load_packages()
  _load_provides()
  _load_requires()
  packages [package_name] = {}
  packages [package_name]['mtime'] = int(modification_time)
  packages [package_name]['size'] = int(filesize)
  provides |= provides_list
  requires [package_name] = requires_list

def find_unresolved ():
  '''
  Module API function

  returns information about all unresolved symbols.
  Should be done via SQL request
  or somehow otherwise quickly and without using all the memory.

  return value is dict: package_name -> list of unsatisfied binary symbol names
  '''
  _load_provides()
  _load_requires()
  ans = {}
  for p in requires:
    unresolved = []
    for l in requires [p]:
      if True or l not in provides:
        unresolved.append(l)
    if unresolved != []:
      ans [p] = unresolved
  return ans

def commit():
  '''
  Module API function

  Stores all memory-cached information to database.
  Сalled once at the end of the whole program to reduce disk usage,
  but this may be changed, if it is more efficient to commit more frequently.
  '''
  global packages
  if not os.path.isdir(dbpath):
    os.mkdir(dbpath)
  fname = os.path.join(dbpath, 'packages')
  file(fname, 'w').write(yaml.safe_dump(packages))
  fname = os.path.join(dbpath, 'provides')
  file(fname, 'w').write(yaml.safe_dump(provides))
  fname = os.path.join(dbpath, 'requires')
  file(fname, 'w').write(yaml.safe_dump(requires))
