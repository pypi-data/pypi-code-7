#!/usr/bin/env python

from setuptools import setup

__version__ = '0.4.2'

CLASSIFIERS = map(str.strip,
"""Environment :: Console
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Natural Language :: English
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2.7
Topic :: Security
""".splitlines())

setup(
    name="geoip-lastlog",
    version=__version__,
    author="Federico Ceratto",
    author_email="federico.ceratto@gmail.com",
    description="GeoIP-based location for the last logins",
    license="GPLv3+",
    url="https://github.com/FedericoCeratto/geoip-lastlog",
    long_description="Parse the output of lastlog and guess city and country name.",
    classifiers=CLASSIFIERS,
    install_requires=[
        'setuptools',
        'arrow',
        'geoip',
        'utmp',
    ],
    platforms=['Linux'],
    entry_points = {
        'console_scripts': ['geoip_lastlog = geoip_lastlog.py']
    }
)
