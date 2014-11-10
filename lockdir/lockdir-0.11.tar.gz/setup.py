#!/usr/bin/env python

from distutils.core import setup

setup(name='lockdir',
      version="0.11",
      description='Lock class based on the creation of directories in a folder',
      author='Carlos de Alfonso',
      author_email='caralla@upv.es',
      url='http://www.grycap.upv.es',
      py_modules = [ 'lockdir' ],
      long_description = "This is a class that tries to limit the number of multiple simultaneous executions of a python script, on a local computer. It works by creating folders (using a pattern) under a folder. If the folder is successfully created, the execution gains the lock. Otherwise the script waits up to a configurable time to try to create the folder.\n\
\n\
Example:\n\
\n\
from lockdir import LockDir\n\
lock = lockdir.LockDir(parallelruns=5, secondswait=300, lockdir=\"/tmp/lockdir.lock\")\n\
if not lock.acquire_lock():\n\
    print \"Error acquiring lock\"\n\
    sys.exit(1)\n\
# do the job\n\
lock.clean_lock()",
      license = "MIT License"
)