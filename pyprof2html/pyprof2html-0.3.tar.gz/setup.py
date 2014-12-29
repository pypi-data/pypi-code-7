#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import sys
sys.path.insert(0, 'pyprof2html')
import pyprof2html

setup(
    name='pyprof2html',
    version=pyprof2html.__version__,
    description="Python cProfile and hotshot profile's data to HTML Converter",
    long_description=open("README.rst").read(),
    license='New BSD License',
    author='Hideo Hattori',
    author_email='hhatto.jp@gmail.com',
    url='http://www.hexacosa.net/project/pyprof2html/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Operating System :: Unix',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
    ],
    keywords="profile visualize html",
    packages=['pyprof2html'],
    package_data={'': ['templates/*']},
    install_requires=['jinja2'],
    zip_safe=False,
    entry_points={'console_scripts': ['pyprof2html = pyprof2html:pyprof2html_main']},
)
