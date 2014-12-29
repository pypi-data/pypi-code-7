#!/usr/bin/env python

from setuptools import setup

from pysimple import _metadata


readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://pysimple.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


setup(
    name='pysimple',
    version=_metadata.__version__,
    description='Python library for Simple online bank',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Tyler Fenby',
    author_email='tylerfenby@gmail.com',
    url='https://github.com/TFenby/pysimple',
    license='GPLv3',
    packages=[
        'pysimple',
    ],
    package_dir={
        'pysimple': 'pysimple',
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'wheel',
        'requests',
        'lxml',
        'click',
    ],
    tests_require=[],
    setup_requires=[],
    cmdclass={},
    keywords='pysimple simple',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
