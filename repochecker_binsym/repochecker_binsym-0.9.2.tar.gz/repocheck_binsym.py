#!/usr/bin/env python
# -*- coding:utf-8 -*-

import repochecker_binsym as rc
import argparse
import sys
import traceback
import os.path

parser = argparse.ArgumentParser(description='ELF repository sanity checker.\n\n'+
'This tool verifies that all required binary symbols can be found in the repository. Note, that this tool knows nothing about package dependencies, so it verifies only the fact that if you install completely all packages from the repository, there will be no errors because of missing binary symbols.')
parser.add_argument('-c', '--config', dest='filename',
                    default=rc.DEFAULT_CONFIG_FNAME,
                    help='Specify the location of the config file (including filename). If there is no such file, it will be created and filled with the default configuration.')

args = parser.parse_args()
rc.configfile = args.filename

if not os.path.exists(rc.configfile):
  try:
    config = rc.gen_config()
    rc.save_config(config, rc.configfile)
    print 'Default configuration has been written to the file %s. Edit it as needed and restart the program.' % rc.configfile
    exit(0)
  except Exception, x:
    print 'Failed to store default configuration to the file %s: %s.\nPlease choose another file (with -c option) and restart the program.' % (rc.configfile, str(x))

def emplace_global_value(key,cfg,subcfg,repo_name):
  '''
  Copy value from global config section to the local one,
  if there is no such section in local config

  key: config key to look for
  cfg: global config
  subcfg: target local config
  repo_name: repo name of local config, for logging only

  returns: True if value has been inserted, False if not
  raises: ValueError if the requested key has not been found neither in global config,
                     nor in local.
  '''
  if key not in subcfg:
    if key not in cfg:
      raise ValueError ('Missing config value for "%s" either in global config section or in the one for %s' %
                        (key, repo_name))
    subcfg [key] = cfg [key]
    return True
  return False

def validate_key_presense(key,cfg,repo_name):
  if key not in cfg:
    raise ValueError ('Missing required config value for "%s" in the section %s' % (key, repo_name))
try:
  config = rc.load_config(rc.configfile)
except Exception, x:
  print 'Failed to load config file %s: %s.\nPlease, select another config using the -c option' % (rc.configfile, str(x))
  exit (0)

for repo in config:
  try:
    repo_name = 'repository %s' % repo['repository']
    global_db_settings = emplace_global_value('db', config, repo, repo_name)
    if not global_db_settings:
      dbcfg = repo ['db']
      emplace_global_value('path', config, dbcfg, repo_name)
      #emplace_global_value('user', config, dbcfg, repo_name)
      #emplace_global_value('pass', config, dbcfg, repo_name)
    else:
      dbcfg = config ['db']
      validate_key_presense('path', dbcfg, 'db (global)')
      #validate_key_presense('user', dbcfg, 'db (global)')
      #validate_key_presense('pass', dbcfg, 'db (global)')
    if 'ignores' not in repo:
      repo ['ignores'] = []
    if 'ignores' in config:
      for i in config ['ignores']:
        repo ['ignores'].append(i)
    rc.process_repository (repo)
  except Exception, x:
    print 'Error processing %s:\n\t%s' % (repo_name, str(x))
    traceback.print_exc (file = sys.stderr)
