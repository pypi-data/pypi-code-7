#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

exec(open("./osm_find_first/_version.py").read())

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'requests'
]

test_requirements = [
    'httpretty',
]

setup(
    name='osm-find-first',
    version=__version__,
    description='Find the first version, incl. datetime, of objects in the OSM database',
    long_description=readme + '\n\n' + history,
    author='Rory McCann',
    author_email='rory@technomancy.org',
    url='https://github.com/rory/osm-find-first',
    packages=[
        'osm_find_first',
    ],
    package_dir={'osm_find_first':
                 'osm_find_first'},
    include_package_data=True,
    install_requires=requirements,
    license="GPLv3+",
    zip_safe=False,
    keywords='osm-find-first',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
