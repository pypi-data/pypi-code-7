from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import pipedrive

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(
    name='pipedrive-python',
    version=pipedrive.__version__,
    url='http://github.com/bellhops/pipedrive-python',
    license='MIT License',
    author='Anthony Blardo',
    tests_require=[],
    install_requires=['mock>=1.0.1',
                      'nose>=1.3.4',
                      'py>=1.4.26',
                      'requests>=2.5.0',
                      'responses>=0.3.0',
                      'six>=1.8.0',
                      ],
    cmdclass={},
    author_email='anthony@blar.do',
    description='Python library for interacting with the Pipedrive API.',
    long_description=long_description,
    packages=['pipedrive'],
    include_package_data=True,
    platforms='any',
    test_suite='nose.collector',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={
    }
)