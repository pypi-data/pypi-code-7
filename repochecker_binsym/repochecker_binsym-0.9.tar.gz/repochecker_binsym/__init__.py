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

from . import storage
from . import logger

import os
import yaml
import libarchive
import elftools
import datetime
import sys

from StringIO import StringIO

from elftools.common.py3compat import bytes2str
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

from traceback import format_exc

def about ():
  print 'This is repochecker: binary symbols'
  print 'Enjoy using it'
  print storage.is_symbol_provided('x')

DEFAULT_CONFIG_FNAME = '/etc/repochecker/binsym.yaml'
configfile = DEFAULT_CONFIG_FNAME

def load_config (filename):
  """
  @brief Load configuration from a given yaml file

  :param filename: where to find config (relative or full path)

  :returns: config (a dictionary: string → value)
  """
  # This is the encoding magic, needed for python 2 so that config strings be utf-8 encoded
  configfile = filename
  def custom_str_constructor(loader, node):
    return loader.construct_scalar(node).encode('utf-8')
  yaml.loader.BaseLoader.add_constructor(u'tag:yaml.org,2002:str', custom_str_constructor)
  try:
    cfg = yaml.load (file (filename, 'r'), Loader=yaml.loader.BaseLoader)
  except:
    cfg = gen_config()
    save_config (cfg, configfile)
  return cfg

def gen_config ():
  """
  @brief Generate default config if none is available

  :returns: config (dictionary: string → value), like that of load_config
  """
  config = []
  config.append({'repository' : '/var/repositories/default',
                 'log' : '/var/log/repochecker/binsymbols/',
                 'db' : {
                    'path': '/var/repochk/binsym.sqlite',
                    # sqlite does not require a user
                    #'user': 'mysql',
                    #'pass': '11111111'
                   },
                 'package-extensions' : ['.rpm'],
                 'ignores' : ['-debug-']})
  return config

def save_config (config, filename):
  """
  @brief save config to a given file

  :returns: None
  """
  yaml.safe_dump(config, file (filename, 'w'))

def get_packages (repo_path, extensions = ['.rpm'], excludes = ['-debug-']):
  tree = os.walk (repo_path);
  for root, dirs, files in tree:
    for f in files:
      ok = False
      # we expect the extensions list to be quite small usually
      for e in extensions:
        if f.endswith (e):
          ok = True
          break
      if '/log/' in root or root.endswith ('/log'):
        continue
      for e in excludes:
        if e in f:
          ok = False
          break
      if ok:
        yield [root, f]

def analyze_packages (directory, extensions, ignores):
  for package in get_packages (directory, extensions, ignores):
    fname = os.path.join(package[0], package[1])
    package_name = package[1]
    print '%s...' % package_name,
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(fname)
    if storage.is_package_analyzed(package_name, mtime, size):
      print '[CACHED]'
      continue
    sys.stdout.flush()
    required = set()
    provided = set()
    try:
      a = libarchive.Archive (fname)
      for f in a:
        if not f.isfile():
          continue
        try:
          stream = StringIO (a.read(f.size))
        except Exception, x:
          print '\t%s: %s' % (f.pathname, str(x))
          continue;
        try:
          elffile = ELFFile(stream)
          #print(' %s sections' % elffile.num_sections())
          section = elffile.get_section_by_name(b'.dynsym')
          if not section or not isinstance(section, SymbolTableSection):
            section = elffile.get_section_by_name(b'.symtab') # debug files
          if not section or not isinstance(section, SymbolTableSection):
            for section in elffile.iter_sections():
              if isinstance(section, SymbolTableSection):
                #print 'Found symbol table:', section.name
                break
          if not section or not isinstance(section, SymbolTableSection):
            #print 'No symbol table found, skipping'
            continue

          num_symbols = section.num_symbols()
          for symbol in section.iter_symbols():
            if symbol.name != '' and \
               symbol.entry['st_shndx'] == 'SHN_UNDEF' and \
               symbol.entry['st_info']['bind'] == 'STB_GLOBAL':
              required.add(symbol.name)
            elif symbol.entry['st_shndx'] != 'SHN_UNDEF':
              provided.add(symbol.name)
          #print(" The name of the last symbol in the section is: %s" % (bytes2str(section.get_symbol(num_symbols - 1).name)))
        except Exception, x:
          #print '\t%s' % str(x)
          continue
      storage.dump_package_info(package_name, mtime, size, required, provided)
      print '[  OK  ]'
    except Exception, e:
      print '[ FAIL ]'
      logger.error(fname, str(e) + format_exc(e))

def process_repository (repo_info):
  """
  @brief Precesses one repository, generates logs for it
  :param repo_info: map:
    repository -> fs path to the repository root
    log -> folder where to store logs
    db -> db info as requested by the storage module

  :returns: None
  """
  start = datetime.datetime.now()
  d = repo_info ['repository']
  storage.init(repo_info ['db'])
  logger.init(repo_info)
  if not os.path.isdir(d):
    print 'ERROR: repository %s does not exist (directory not found)' % d
    return
  analyze_packages(d, repo_info ['package-extensions'], repo_info ['ignores'])
  analyzed = datetime.datetime.now()
  verdict = storage.find_unresolved()
  if verdict != []:
    prev_pack = verdict[0][0]
    missing_symbols = []
    for package, details in verdict:
      if package == prev_pack:
        missing_symbols.append(str(details))
      else:
        logger.log_package_details (str(prev_pack), missing_symbols)
        missing_symbols = [str(details)]
        prev_pack = package
  dependencies_found = datetime.datetime.now()
  data_saved = datetime.datetime.now()

  print
  print '*** READY ***'
  total_delta = (data_saved - start).total_seconds()
  delta1 = (analyzed - start).total_seconds()
  print 'Analysis took %.4f s,' % delta1, '%.2f%%' % (100.* delta1 / total_delta)
  delta1 = (dependencies_found - analyzed).total_seconds()
  print 'Dependency calculation took %.4f s,' % delta1, '%.2f%%' % (100. * delta1 / total_delta)
  delta1 = (data_saved - dependencies_found).total_seconds()
  print 'DB write took %.4f s,' % delta1, '%.2f%%' % (100. * delta1 / total_delta)
  print
  print 'Overall working time: %.4f s,' % total_delta
