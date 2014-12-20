#coding: utf-8
from setuptools import setup

setup(
    version='0.1.1',
    name = "findbak",
    packages = ['findbak'],
    description='File list backup',
    author='Jakob Hedman',
    author_email='jakob@hedman.email',
    maintainer='Jakob Hedman',
    maintainer_email='jakob@hedman.email',
    license='GNU GPLv3',
    url='https://github.com/spillevink/findbak',
    package_dir = {'findbak':'findbak'},
    entry_points = {
        'console_scripts': [
            'findbak = findbak.findbak:main.command',
        ],
    },
    long_description = open('README.rst').read(),
)
