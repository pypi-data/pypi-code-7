#!/usr/bin/env python

from setuptools import setup, find_packages

from swuploader import __version__

setup(
    name='swuploader',
    version=__version__,
    author='Brett Langdon',
    author_email='brett@blangdon.com',
    packages=find_packages(),
    install_requires=[
        'shapeways==1.0.0',
    ],
    scripts=[
        './bin/swuploader',
    ],
    setup_requires=[],
    description='Easy to use bulk model uploader for Shapeways.com API',
    url='http://github.com/brettlangdon/swuploader',
)
