#!/usr/bin/env python

VERSION     = '1.0.0'
DESCRIPTION = 'Thin wrapper for integrating ZeroMQ sockets into the Twisted reactor'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name             = 'zed',
    version          = VERSION,
    description      = DESCRIPTION,
    license          = "MIT",
    long_description ="""\
Thin wrapper for integrating ZeroMQ sockets into the Twisted reactor
""",
    url              = 'https://github.com/cocagne/zed',
    author           = "Tom Cocagne",
    author_email     = 'tom.cocagne@gmail.com',
    install_requires = ['twisted>=14.0'],
    provides         = ['zed'],
    py_modules       = ['zed'],
    keywords         = ['zeromq', 'twisted'],
    classifiers      = ['Development Status :: 4 - Beta',
                        'Framework :: Twisted',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: MIT License',
                        'Operating System :: POSIX',
                        'Programming Language :: Python',
                        'Topic :: Software Development :: Libraries',
                        'Topic :: System :: Networking'],
    )

