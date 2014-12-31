#!/usr/bin/env python
"""
Install django-quiet-runserver using setuptools
"""

from djangoquietrunserver import __version__

from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    README = f.read()

setup(
    name='django-quiet-runserver',
    version=__version__,
    description='Quieter runserver for Django',
    long_description=README,
    author='Tim Heap',
    author_email='tim@timheap.me',
    url='https://bitbucket.org/tim_heap/django-quiet-runserver',

    install_requires=['Django>=1.6'],
    zip_safe=True,

    packages=find_packages(),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
