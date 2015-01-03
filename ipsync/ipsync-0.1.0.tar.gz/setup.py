#!/usr/bin/env python

"""
Setup script for ip_sync.
"""

import setuptools

from ip_sync.version import __project__, __version__

import os
if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = ""  # a placeholder, readme is generated on release
CHANGES = open('CHANGES.md').read()


setuptools.setup(
    name=__project__,
    version=__version__,

    description='ipsync is a script to update multiple '
                'cloud DNS providers with your external IP address',
    url='https://github.com/jon-walton/ipsync',
    author='Jon Walton',
    author_email='jonwalton@gmail.com',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': ['ipsync = ip_sync.main:main']},

    long_description=(README + '\n' + CHANGES),
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
    ],

    install_requires=open('requirements.txt').readlines(),
)
