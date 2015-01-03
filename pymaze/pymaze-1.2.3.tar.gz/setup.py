#!/usr/bin/env python
# coding: utf8

import os
import setuptools
import sys


# The name of the package on PyPi
PYPI_PACKAGE_NAME = 'pymaze'

# The name of the main Python package
MAIN_PACKAGE_NAME = 'maze'

# The package URL
PACKAGE_URL = 'https://github.com/moses-palmer/maze.py'

SCRIPTS = ['tools/amaze']

# The author email
AUTHOR_EMAIL = 'moses.palmer@gmail.com'


def setup(**kwargs):
    setuptools.setup(
        name = PYPI_PACKAGE_NAME,
        version = '.'.join(str(i) for i in INFO['version']),
        description = ''
            'A library to generate and display mazes',
        long_description = README + '\n\n' + CHANGES,

        install_requires = [
            'cairocffi >=0.6'],
        setup_requires = [],

        author = INFO['author'],
        author_email = AUTHOR_EMAIL,

        url = PACKAGE_URL,

        packages = setuptools.find_packages(
            os.path.join(
                os.path.dirname(__file__),
                'lib'),
            exclude = ['tests', 'tests.suites']),
        scripts = SCRIPTS,
        package_dir = {'': 'lib'},
        zip_safe = True,

        license = 'GPLv3',
        classifiers = [],

        **kwargs)


# Arguments passed to setup
setup_arguments = {}


# Read globals from ._info without loading it
INFO = {}
with open(os.path.join(
        os.path.dirname(__file__),
        'lib',
        'maze',
        '_info.py')) as f:
    for line in f:
        try:
            name, value = (i.strip() for i in line.split('='))
            if name.startswith('__') and name.endswith('__'):
                INFO[name[2:-2]] = eval(value)
        except ValueError:
            pass


try:
    # Read README
    with open(os.path.join(
            os.path.dirname(__file__),
            'README.rst')) as f:
        README = f.read()


    # Read CHANGES
    with open(os.path.join(
            os.path.dirname(__file__),
            'CHANGES.rst')) as f:
        CHANGES = f.read()
except IOError:
    README = ''
    CHANGES = ''


try:
    setup(**setup_arguments)
except Exception as e:
    try:
        sys.stderr.write(e.args[0] % e.args[1:] + '\n')
    except:
        sys.stderr.write(str(e) + '\n')
