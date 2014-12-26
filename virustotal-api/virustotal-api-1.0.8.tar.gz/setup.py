#!/usr/bin/env python
import os
import sys

from setuptools import setup

import virus_total_apis

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('doc/README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()

setup(name='virustotal-api'
        ,version=virus_total_apis.__version__
        ,description='Virus Total Public/Private/Intel API'
        ,long_description=readme + '\n\n' + history
        ,url='https://github.com/blacktop/virustotal-api'
        ,author='blacktop'
        ,author_email='dev@blacktop.io'
        ,license=virus_total_apis.__license__
        ,test_suite="tests"
        ,packages=['virus_total_apis']
        ,package_dir={'virus_total_apis': 'virus_total_apis'}
        ,install_requires=["requests >= 2.2.1"])
