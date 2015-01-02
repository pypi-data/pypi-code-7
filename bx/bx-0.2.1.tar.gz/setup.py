#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'bx',
    'description': 'Simple in-memory storage for Python',
    'long_description': open('README.md').read(),
    'author': 'Ty-Lucas Kelley',
    'url': 'https://github.com/tylucaskelley/bx-python',
    'download_url': 'https://github.com/tylucaskelley/bx-python/tarball/v0.2.1',
    'author_email': 'tylucaskelley@gmail.com',
    'license': 'MIT',
    'version': '0.2.1',
    'install_requires': [
        'nose',
        'jsonschema'
    ],
    'packages': [
        'bx'
    ],
    'classifiers': [
        'Programming Language :: Python',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
}

setup(**config)
