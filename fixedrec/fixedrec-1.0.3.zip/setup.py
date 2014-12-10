#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""fixedrec - Fixed size record IO
"""

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Topic :: Software Development :: Libraries
"""

import setuptools
from distutils.core import setup, Command


version = '1.0.3'


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name='fixedrec',
    version=version,
    requires=[],
    install_requires=[],
    url='https://github.com/thebjorn/fixedrec',
    author='Bjorn Pettersen',
    author_email='bp@norsktest.no',
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.rst').read(),
    cmdclass={'test': PyTest},
    packages=['fixedrec'],
    zip_safe=False,
)
