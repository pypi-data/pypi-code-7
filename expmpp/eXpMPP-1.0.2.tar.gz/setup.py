#!/usr/bin/env python
from setuptools import setup

setup(
    name='eXpMPP',
    version='1.0.2',
    author='Louis Thibault',
    author_email='louist87@gmail.com',
    packages=['expmpp'],
    include_package_data=True,
    install_requires=['xmpppy'],
    url='https://github.com/louist87/expmpp',
    license='GPLv3.0',
    description=('XMPP notifications for psychology experiments'),
    keywords=['experiment', 'psychology', 'XMPP', 'google talk'],
    long_description=open('README.md').read()
)
