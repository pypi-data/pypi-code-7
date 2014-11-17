#!/usr/bin/env python2

from distutils.core import setup

from avena import avena


_classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: ISC License (ISCL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    'Topic :: Multimedia :: Graphics',
]

with open('README.rst', 'r') as rst_file:
    _long_description = rst_file.read()

_setup_args = {
    'author':           avena.__author__,
    'author_email':     avena.__email__,
    'classifiers':      _classifiers,
    'description':      avena.__doc__,
    'license':          avena.__license__,
    'long_description': _long_description,
    'name':             'Avena',
    'url':              'https://bitbucket.org/eliteraspberries/avena',
    'version':          avena.__version__,
}


if __name__ == '__main__':

    setup(packages=['avena'],
          **_setup_args)
