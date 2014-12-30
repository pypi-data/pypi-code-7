# -*- coding: utf-8 -*-

import qjson
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('README.md', 'r') as f:
    readme = f.read()

history = 'first upload to pypi'


setup(
    name='qjson',

    description='quick and dirty way to convert json string to python object',
    long_description=readme + '\n\n' + history,

    url='https://github.com/jatsz/qjson',
    download_url='https://github.com/jatsz/qjson/tarball/master',

    version=qjson.__version__,
    license=qjson.__license__,

    author=qjson.__author__,
    author_email='imjatsz@gmail.com',

    packages=['qjson'],

    classifiers=[],

    keywords = "json",

)