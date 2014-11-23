#!/usr/bin/env python
from setuptools import setup
from beans import __version__

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.md').read()
except:
    pass

setup(
    name='beans',
    version=__version__,
    description='The Python client library for the Beans API',
    author='Beans',
    author_email='contact@loyalbeans.com',
    url='https://github.com/loyalbeans/Beans-API-Python',
    download_url='https://github.com/loyalbeans/Beans-API-Python/tarball/v1.2.0',
    license='Apache',
    packages=['beans'],
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[
        'requests>=2.4.2'
    ],
)