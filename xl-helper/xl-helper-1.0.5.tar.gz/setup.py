#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='xl-helper',
    version='1.0.5',
    description='XL Deploy helper',
    long_description='This tool helps with installation and upgrade of XL Deploy and plugins',
    author='Mike Kotsur',
    author_email='mkotsur@xebialabs.com',
    url='http://xebialabs.com/',
    packages=find_packages(where=".", exclude=["tests*"]),
    package_data={'xl_helper': ['deployit.conf', '.xl-helper.defaults']},
    include_package_data=True,
    install_requires=['jenkinsapi', 'argparse', 'pytz'],
    scripts=['xl-helper']
)
