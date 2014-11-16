#!/usr/bin/env python

from setuptools import setup

setup(
    name='vimix',
    version='0.0.2',
    packages=['vimix'],
    scripts=['scripts/vimix'],
    package_data={
        '': ['templates/*.txt'],
    },
    author='boku',
    author_email='punipuniomochi@gmail.com',
    description='Make minimum environment for Vim script',
    license='WTFPL',
    url='https://github.com/mtwtkman/vimix',
    download_url='https://github.com/mtwtkman/vimix/tarball/master',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development"
    ],
)
