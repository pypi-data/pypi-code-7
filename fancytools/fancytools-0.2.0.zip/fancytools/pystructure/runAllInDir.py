# -*- coding: utf-8 -*-

import os
import pkgutil
import runpy


thismodname = __name__.split('.')[-2:]
thismodname = '.'.join(thismodname)


# Note there is a bug in pkgutil.walk_packages
# excluding all modules that have the same name as modules in 
# the standard library, see
# http://bugs.python.org/issue14787
# that's why 'os' and 'math' are not tested at the moment

def runAllInDir(dir_path, exclude=[]):
	'''
	execute all modules as __main__ within a given package path 
	'''
	print 'testing all modules of %s' %dir_path
	for _, modname, ispkg in pkgutil.walk_packages(
			[dir_path],
			#onerror=lambda x: None
			):
		if not ispkg and modname != thismodname and not modname in exclude: # don't test this module
			print '... %s' %modname
			runpy.run_module(modname, init_globals=None, run_name='__main__', alter_sys=False)

