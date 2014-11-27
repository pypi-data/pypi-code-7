# -*- coding: utf-8 -*-

from setuptools import setup

import direg

# README.rst dynamically generated:
with open('README.rst', 'w') as f:
    f.write(direg.__doc__)


def read(file):
    with open(file, 'r') as f:
        return f.read().strip()

setup(
    name='direg',
    version=read('VERSION'),
    description=('A drop-in registry. Easily maintain a central configuration registry for your complex '
                 'python project.'),
    long_description=read('README.rst'),
    author='Mike Burr',
    author_email='mburr@unintuitive.org',
    url='https://github.com/stnbu/direg',
    download_url='https://github.com/stnbu/direg/archive/master.zip',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    packages=['direg'],
    keywords=['configuration', 'registry', 'refactor'],
    test_suite='nose.collector',
    test_requires=['nose'],
)
