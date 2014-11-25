#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


from rco import __version__


def main ():
    setup (
        name = 'python-rco',
        version = __version__,
        description = 'RC Online services library',
        long_description = 'RC Online services library',
        author = 'Ruslan V. Uss',
        author_email = 'unclerus@gmail.com',
        # url = 'https://github.com/UncleRus/cherryBase',
        license = 'BSD',
        packages = ('rco', 'rco.client', 'rco.service'),
        install_requires = ('cherrybase >= 0.3.8')
    )


if __name__ == "__main__":
    main ()
