#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'bx',
    'version': '0.3.0',
    'description': 'Simple in-memory storage for Python',
    'long_description': open('README.md').read(),
    'author': 'Ty-Lucas Kelley',
    'url': 'https://github.com/tylucaskelley/bx-python',
    'download_url': 'https://github.com/tylucaskelley/bx-python/tarball/v0.3.0',
    'author_email': 'tylucaskelley@gmail.com',
    'license': 'MIT',
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
