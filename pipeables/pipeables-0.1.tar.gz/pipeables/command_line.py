#!/usr/bin/env python

import os
import json
#import pkgutil
import inspect
import imp

import sys

#the base query all queries inherit from
from base import BaseQuery

#get the path to the users q directory of queries
from os.path import expanduser
home = expanduser("~")


required_properties = ['proj','name','q','params','db']
queries = {}
sys.path.append(home+"/q1")
for f in os.listdir(home+"/q1"):
  if f.endswith(".py") and f != '__init__.py':
    m = f.replace(".py","")
    a,b,c = imp.find_module(m)
    t = imp.load_module(m,a,b,c)
    for k,v in t.__dict__.iteritems():
      if inspect.isclass(v):
        keys = map(lambda x: x[0], inspect.getmembers(v))
        if len(required_properties) == len(set(keys) & set(required_properties)):
          if v.proj not in queries.keys():
            queries[v.proj] = {}
          queries[v.proj][v.name] = v




PROJFILE= 'proj.json'

def pipeable():

  if not os.path.isfile(home+"/dbconf.json"):
    print "Can't find dbconf.json in the home direcotry :"+home
  else:
    f = open(home+"/dbconf.json","r")
    conf = json.loads(f.read())

    if PROJFILE in os.listdir('.'):
      f = open(PROJFILE,"r")
      proj = json.load(f)['proj']
      query = sys.argv[1]
      if query in queries[proj]:
        print "got a query"

        class runStuff(BaseQuery):
          """anonymous runner"""

        _run = runStuff(**queries[proj][query].__dict__)
        lines = _run.query(sys.argv[2:])
        if len(lines) > 0:
          print "\n".join(lines)
        _run.storeResult("\n".join(lines))

      else:
        print "couldn't find query"
    else:
      print "No Project Set"

def makeList():
  _list = []
  if sys.stdin.isatty() == False:
    for l in sys.stdin.readlines():
      _list.append("'"+l.replace("'","''").strip()+"'")

  print ",".join(_list)

def makeValueList():

  _list = []
  if sys.stdin.isatty() == False:
    for l in sys.stdin.readlines():
      _list.append("("+",".join(map(lambda a: "'"+a.replace("'","''").strip()+"'",l.split("\t")))+")")

  print ",".join(_list)

def intersection():
  file_names = sys.argv[1:]
  files = []

  for fn in file_names:
    f = open(fn,'r')
    files.append({
      'file' : fn,
      'lines' : f.readlines()
    })

  result = {}
  for f in files:
    for l in f['lines']:
      c = l.strip()
      if c in result:
        result[c][f['file']] = 1
      else:
        result[c] = { f['file'] : 1 }


  for k in result.keys():
    line = [k]
    for fn in file_names:
      if fn in result[k]:
        line.append("1")
      else:
        line.append("0")

    print "\t".join(line)



