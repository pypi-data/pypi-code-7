#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


test_requires = [
    'coverage',
    'pytest',
    'pytest-cov>=1.4',
    'pytest-flakes',
    'pytest-pep8',
    'python-coveralls',
]


install_requires = []


dev_requires = [
    'flake8>=2.0',
    'invoke',
    'twine'
]


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='markey',
    description='Markup parser',
    long_description=read('README.rst') + u'\n\n' + read('CHANGELOG.rst'),
    version='0.5',
    license='BSD',
    author='Christopher Grebs',
    author_email='cg@webshox.org',
    url='http://github.com/EnTeQuAk/markey/',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    tests_require=test_requires,
    install_requires=install_requires,
    cmdclass={'test': PyTest},
    extras_require={
        'docs': ['sphinx'],
        'tox': ['tox'],
        'tests': test_requires,
        'dev': dev_requires,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
