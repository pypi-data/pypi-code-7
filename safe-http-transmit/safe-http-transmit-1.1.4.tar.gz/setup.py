#!/usr/bin/env python
from distutils.core import setup
readme = open('README.rst').read()

setup(
    name='safe-http-transmit',
    version='1.1.4',
    author_email='gattster@gmail.com',
    author='Philip Gatt',
    description="A safe HTTP transmitter.",
    long_description=readme,
    url='http://github.com/defcube/safe-http-transmit',
    package_dir={'safe_http_transmit': 'lib'},
    packages=['safe_http_transmit'],
    data_files=[('', ['README.rst'])],
    )