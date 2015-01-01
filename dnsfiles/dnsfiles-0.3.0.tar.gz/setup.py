#!/usr/bin/env python

from distutils.core import setup
import versioneer

versioneer.VCS = 'git'
versioneer.versionfile_source = 'dnsfiles/_version.py'
versioneer.versionfile_build = 'dnsfiles/_version.py'
versioneer.tag_prefix = '' # tags are like 1.2.0
versioneer.parentdir_prefix = 'dnsfiles-' # dirname like 'myproject-1.2.0'

setup(name='dnsfiles',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Managing GANDI DNS from the file system.',
      author='Jared Bunting',
      author_email='jared.bunting@peachjean.com',
      url='https://github.com/peachjean/dnsfiles',
      packages=['dnsfiles'],
      scripts=['scripts/dnsfiles-init', 'scripts/dnsfiles-sync'],
      install_requires=['pyyaml>=3.11'],
     )
