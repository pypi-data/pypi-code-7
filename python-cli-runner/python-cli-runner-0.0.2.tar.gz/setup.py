#!/usr/bin/env python

from setuptools import setup


from src import __version__


setup(
    name='python-cli-runner',
    version=__version__,
    description='Toolkit that organize multiple entry points of your codebase with Docopt powerful.',
    url='https://github.com/alexey-grom/python-cli-runner',
    author='alxgrmv@gmail.com',
    packages=['cli_runner'],
    package_dir={'cli_runner': 'src/cli_runner'},
    install_requires=[
        'docopt',
        'six',
    ],
)
