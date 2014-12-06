#!/usr/bin/env python

"""
Setup script for curmit.
"""

import setuptools

from curmit import __project__, __version__, CLI

import os
if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = ""
CHANGES = open('CHANGES.md').read()

setuptools.setup(
    name=__project__,
    version=__version__,

    description="Grabs text from a URL and commits it.",
    url='https://github.com/jacebrowning/curmit',
    author='Jace Browning',
    author_email='jacebrowning@gmail.com',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': [CLI + ' = curmit.curmit:main']},

    long_description=(README + '\n' + CHANGES),
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Version Control',
    ],

    install_requires=open('requirements.txt').readlines(),
)
