#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from webdav.client import __version__ as version

setup(
    name     = 'webdavclient',
    version  = version,
    packages = find_packages(),
    requires = ['python (>= 2.7.6)'],
    install_requires=['pycurl', 'lxml', 'argcomplete'],
    scripts = ['wdc'],
    description  = 'Webdav API, resource API и wdc для WebDAV-серверов (Yandex.Disk, Dropbox, Google Disk, Box, 4shared и т.д.)',
    long_description = open('README.rst').read(),
    author = 'Designerror',
    author_email = 'designerror@yandex.ru',
    url          = 'https://github.com/designerror/webdavclient',
    download_url = 'https://github.com/designerror/webdavclient/tarball/master',
    license      = 'MIT License',
    keywords     = 'webdav, client, python, module, library, packet, Yandex.Disk, Dropbox, Google Disk, Box, 4shared',
    classifiers  = [
        'Environment :: Console',
        'Environment :: Web Environment', 
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
