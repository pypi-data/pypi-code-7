#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
import re
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


REQUIRES = [
    'docopt',
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version("parsedoc/__init__.py")


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='parsedoc',
    version=__version__,
    description='Parses PHP doc blocks into markdown',
    long_description=(read("README.rst") + "\n\n" +
                      read("HISTORY.rst").replace('.. :changelog:', '')),
    author='Thom Wiggers',
    author_email='thom@thomwiggers.nl',
    url='https://github.com/thomwiggers/parsedoc',
    install_requires=REQUIRES,
    license="\n"+read("LICENCE"),
    zip_safe=False,
    keywords='parsedoc php',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    packages=['parsedoc'],
    entry_points={
        'console_scripts': [
            "parsedoc = parsedoc:main"
        ]
    },
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
