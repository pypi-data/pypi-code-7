#!/usr/bin/env python

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

from pysimple import version


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://pysimple.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


setup(
    name='pysimple',
    version=version.__version__,
    description='Python library for Simple online bank',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Tyler Fenby',
    author_email='tylerfenby@gmail.com',
    url='https://github.com/TFenby/pysimple',
    license='GPLv3',
    packages=[
        'pysimple',
    ],
    package_dir={
        'pysimple': 'pysimple',
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'wheel',
        'requests',
        'lxml',
    ],
    tests_require=['pytest'],
    setup_requires=[],
    cmdclass={'test': PyTest},
    keywords='pysimple simple',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
