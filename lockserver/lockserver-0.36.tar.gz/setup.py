#!/usr/bin/env python
from distutils.core import setup

setup(name='lockserver',
      version="0.36",
      description='Simple lock server and client api for distributed coordination using a simple centralized python lock server',
      author='Carlos de Alfonso',
      author_email='caralla@upv.es',
      url='http://www.grycap.upv.es',
      py_modules = [ 'config', 'lockcli', 'rpcweb' ],
      scripts = [ 'lockserver' ],
      data_files = [ ('/etc/lockserver/', ['etc/lockserver.conf'] ),
        ('/etc/init.d/', ['lockd'] ),
        ('/etc/logrotate.d/', ['etc/lockserver'] ),
        ],
      long_description = "",
      install_requires = [ 'web.py>=0.37' ],
      license = "MIT"
)
