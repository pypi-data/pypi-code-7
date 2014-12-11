#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

settings = dict()

setup(
    name='csample',
    version='0.1.0',
    description='Consistent sampling library for Python',
    long_description=open('README.rst').read(),
    author='Alan Kang',
    author_email='alankang@boxnwhis.kr',
    url='https://github.com/box-and-whisker/csample',
    py_modules=['csample'],
    package_data={'': ['README.rst']},
    include_package_data=True,
    install_requires=['six', 'xxhash'],
    tests_require=['coverage', 'mock', 'nose'],
    test_suite='tests',
    license='MIT License',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Text Processing :: Filters',
    ],
    entry_points={
        'console_scripts': [
            'csample=csample:main',
        ],
    },
)
