#!/usr/bin/env python2

'''Overwatch: Python Logging Browser.'''

from distutils.core import setup
from setuptools import find_packages

classifiers = '''
Development Status :: 4 - Beta
Environment :: Console
Environment :: X11 Applications :: GTK
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: System Administrators
License :: OSI Approved :: GNU General Public License v2 (GPLv2)
Operating System :: POSIX :: Linux
Programming Language :: Python :: 2.7
Topic :: Software Development :: Debuggers
Topic :: System :: Monitoring
'''

doclines = __doc__.split('\n')

long_desc = open('README.rst', 'r').read()

setup(name='overwatch',
        version='2.0.0',
        author='Andrew Dunai',
        author_email='me@andrewdunai.com',
        url='http://andrewdunai.com/projects/overwatch/',
        packages=find_packages(),
        package_data={'overwatch': ['data/libs/*.js', 'data/*.html', 'data/*.css', 'data/*.js']},
        platforms=['unix'],
        classifiers=filter(None, classifiers.split("\n")),
        description=doclines[0],
        long_description=long_desc,
        install_requires=['gevent', 'Flask', 'flask-socketio', 'pytz'],
    )
