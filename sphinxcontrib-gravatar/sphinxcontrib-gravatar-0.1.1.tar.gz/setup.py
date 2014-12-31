# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


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


long_description = '\n'.join([
    open(os.path.join(".", "README.rst")).read(),
    open(os.path.join(".", "AUTHORS.rst")).read(),
    open(os.path.join(".", "HISTORY.rst")).read(),
])

requires = ['Sphinx>=1.2']

tests_require = [
    "pytest-cov",
    "pytest",
    "mock",
]

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Documentation',
    'Topic :: Utilities',
]

setup(
    name='sphinxcontrib-gravatar',
    version='0.1.1',
    url='https://github.com/tell-k/sphinxcontrib-gravatar',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-gravatar',
    license='BSD',
    author='tell-k',
    author_email='ffk2005 at gmail.com',
    description='Sphinx "gravatar" extension',
    long_description=long_description,
    zip_safe=False,
    classifiers=classifiers,
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    namespace_packages=['sphinxcontrib'],
)
