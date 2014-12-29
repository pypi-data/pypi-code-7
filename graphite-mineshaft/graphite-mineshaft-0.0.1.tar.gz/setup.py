#!/usr/bin/env python
"""
graphite-mineshaft
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2014 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup

install_requires = ['mineshaft']


with open('README.rst') as f:
    long_description = f.read()


setup(
    name='graphite-mineshaft',
    version='0.0.1',
    author='Matt Robenolt',
    author_email='matt@ydekproductions.com',
    url='https://github.com/mattrobenolt/graphite-mineshaft',
    description='Graphite backend for Mineshaft',
    license='BSD',
    long_description=long_description,
    py_modules=['graphite_mineshaft.finders'],
    install_requires=install_requires,
    zip_safe=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
)
