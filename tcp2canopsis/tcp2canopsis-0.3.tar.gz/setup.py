#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='tcp2canopsis',
    version='0.3',
    license='MIT',

    author='David Delassus',
    author_email='david.jose.delassus@gmail.com',
    description='Canopsis Connector which listen for JSON events on TCP port',
    url='https://github.com/linkdd/tcp2canopsis',
    download_url='https://github.com/linkdd/tcp2canopsis/tarball/0.2',
    keywords=['canopsis'],
    classifiers=[],

    scripts=['scripts/tcp2canopsis'],
    packages=find_packages(),
    install_requires=[
        'argparse>=1.2.1',
        'Twisted>=14.0.2',
        'kombu>=3.0.21'
    ]
)
