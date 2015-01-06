#!/usr/bin/env python

from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name = 'pbook',
    version = '1.0',
    description = 'LDAP phonebook written in Python',
    author = 'Jiri Tyr',
    author_email = 'jiri.tyr@gmail.com',
    url = 'http://github.com/jtyr/pbook',
    license = 'MIT',
    keywords = 'phonebook ldap',
    platforms = ['any'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP'
    ],
    long_description = long_description,
    scripts=['pbook'],
    install_requires = ['ldap'],
    data_files = [
        ('etc', ['pbook.conf']),
        ('share/doc/pbook', ['LICENSE', 'README.md'])
    ]
)
