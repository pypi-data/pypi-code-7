#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name             = 'yakindlestrip',
    version          = '1.36',
    description      = 'yet another pip-installable conversion of Paul Durrant\'s kindlestrip',
    long_description = 'more info please check http://www.mobileread.com/forums/showthread.php?t=96903',
    author           = 'Zigler Zhang',
    author_email     = 'zigler.zhang@gmail.com',
    url              = 'https://github.com/fireinice/yakindlestrip',
    license          = open("LICENSE").read(),
    scripts         = ['kindlestrip.py'],

    classifiers      = (
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Build Tools'
    ),
)
