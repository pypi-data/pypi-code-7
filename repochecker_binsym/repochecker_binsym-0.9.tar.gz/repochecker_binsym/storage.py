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
# done!
# import yaml
import os
import sqlite3

# All the variables below are for internal module use only,
# they will be changed in next releases

# dbpath stores database name
config = None
dbpath = ''
db = None

def init (cfg):
  global dbpath, db
  '''
  Module API function

  Specify config for further module operation.
  Config needs to be a map for one given repository
  Config contains at lease value «db» with database file path or database name
  '''
  global config
  config = cfg
  dbpath = cfg ['path']
  # Open database connection
  db = sqlite3.connect(dbpath)
  print "Opened database successfully";
  # prepare a cursor object using cursor() method
  cursor = db.cursor()
  cursor.execute('''CREATE TABLE IF NOT EXISTS Requires
       (package        TEXT    NOT NULL,
        symbol         TEXT    NOT NULL);''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS Provides
       (package        TEXT    NOT NULL,
        symbol         TEXT    NOT NULL);''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS Packages
       (package        TEXT    NOT NULL,
        mtime          TEXT    NOT NULL,
        size           INT     NOT NULL);''')

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
  cursor = db.cursor()
  cursor.execute('SELECT package FROM Packages \
    WHERE package == "%s" AND mtime == "%s" AND size == %d;' % (str(package_name), str(modification_time), filesize))
  return cursor.fetchall() != []

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
  #print "Opened database successfully";
  # prepare a cursor object using cursor() method
  cursor = db.cursor()
  cursor.execute ('DELETE FROM Provides WHERE package = "%s"' % str(package_name))
  cursor.execute ('DELETE FROM Requires WHERE package = "%s"' % str(package_name))
  for r in requires_list:
    query = 'INSERT INTO Requires (package,symbol) \
      VALUES ("%s", "%s");' % (package_name, r)
    cursor.execute(query);
  for p in provides_list:
    cursor.execute('INSERT INTO Provides (package,symbol) \
      VALUES ("%s", "%s");' % (package_name, p));
  cursor.execute ('INSERT INTO Packages \
      VALUES ("%s", "%s", %d)' % (str (package_name), str (modification_time), filesize))
  db.commit()

def find_unresolved ():
  '''
  Module API function

  returns information about all unresolved symbols.
  Should be done via SQL request
  or somehow otherwise quickly and without using all the memory.

  return value is dict: package_name -> list of unsatisfied binary symbol names
  '''
  # Open database connection
  cursor = db.cursor()
  cursor.execute('SELECT * FROM Requires t1 WHERE t1.symbol NOT IN (SELECT symbol FROM Provides);')
  # Fetch all the rows in a list of lists.
  ans = cursor.fetchall()
  print "We've got the answer!"
  return ans
