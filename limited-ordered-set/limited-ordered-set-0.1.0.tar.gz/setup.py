#!/usr/bin/env python
import os

from setuptools import setup, find_packages

VERSION = (0, 1, 0)


def get_version():
    return ".".join(map(str, VERSION))


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='limited-ordered-set',
    version=get_version(),
    author='Alexandr Shurigin',
    author_email='alexandr.shurigin@gmail.com',
    description='Limited Ordered Set object. Data type for storing actions history lists.',
    license='BSD',
    keywords='collection library type set list limited',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    test_suite='tests',
    url='https://github.com/phpdude/limited-ordered-set',
    long_description=read("README.rst"),
    classifiers=[
        'Intended Audience :: Information Technology',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ], install_requires=['ordered-set']
)