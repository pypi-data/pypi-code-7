#!/usr/bin/env python

from distutils.core import setup

setup(name='dnsfiles',
      version='0.2.0',
      description='Managing GANDI DNS from the file system.',
      author='Jared Bunting',
      author_email='jared.bunting@peachjean.com',
      url='https://github.com/peachjean/dnsfiles',
      packages=['dnsfiles'],
      scripts=['scripts/dnsfiles-init', 'scripts/dnsfiles-sync'],
      install_requires=['pyyaml>=3.11'],
     )
