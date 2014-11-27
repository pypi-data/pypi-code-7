# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from data_uri import __version__, __author__, __author_email__, __description__, __license__

setup(
    name='data_uri',
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    license=__license__,
    packages=["data_uri"],
    install_requires=[
        'python-magic',
    ],
    entry_points={
        'console_scripts': [
            'data_uri = data_uri.__main__:run',
        ],
    }
)

