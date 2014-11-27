# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from tornado_data_uri import __version__, __author__, __author_email__, __description__, __license__

setup(
    name='tornado_data_uri',
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    license=__license__,
    packages=["tornado_data_uri"],
    install_requires=[
        'tornado',
        'data_uri',
    ],
    entry_points={
        'console_scripts': [
            'tornado_data_uri = tornado_data_uri.__main__:run',
        ],
    }
)

