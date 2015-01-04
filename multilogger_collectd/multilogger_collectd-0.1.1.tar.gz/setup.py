""" Packaging for multilogger_collectd """

import io
import os
import re

from setuptools import setup


def read(*names, **kwargs):
    """ Read file relative to the directory where this file is located """
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


URL = 'https://github.com/pka/arexx-multilogger-collectd-plugin'
setup(
    name='multilogger_collectd',
    packages=['multilogger_collectd'],
    version='0.1.1',
    license='GPLv2',
    description='A collectd plugin for monitoring AREXX Multiloggers',
    long_description=read('README.rst'),
    author='Pirmin Kalberer',
    author_email='pka@sourcepole.ch',
    url=URL,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
    ],
    keywords='AREXX multilogger collectd',
    install_requires=[
        'pyusb'
    ],
)
