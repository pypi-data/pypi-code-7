#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()

requirements = map(str.strip, open('requirements.txt').readlines())

VERSION = open('VERSION').read().strip()

setup(
    name='nose-sqlcapture',
    version=VERSION,
    description='Capture SQL queries being generated from a nosetests run',
    long_description=readme + '\n\n',
    author='Kevin J. Qiu',
    author_email='kevin@freshbooks.com',
    url='https://github.com/freshbooks/nose-sqlcapture',
    packages=[
        'sqlcapture',
    ],
    package_dir={'sqlcapture': 'sqlcapture'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='nose-sqlcapture',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    entry_points={
        'nose.plugins.0.10': [
            'sqlcapture = sqlcapture:SQLCapture'
        ]
    },
)
