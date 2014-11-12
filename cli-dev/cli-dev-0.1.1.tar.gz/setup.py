#!/usr/bin/env python

from setuptools import setup
from dev import __version__

with open('README.rst') as f:
    readme = f.read()

setup(name='cli-dev',
    version=__version__,
    description='Register and run a command for each directory',
    long_description=readme,
    author='Eddie Antonio Santos',
    author_email='easantos@ualberta.ca',
    url='https://github.com/eddieantonio/dev',
    py_modules=['dev'],
    entry_points={
        'console_scripts': [
            'dev = dev:main'
        ]
    },
    keywords=['testing', 'shell', 'cwd'],
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: Freely Distributable',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: System :: Systems Administration',
    ]
)
