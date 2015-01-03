from distutils.core import setup

long_description = """Summary
==========
**DummyMP** is a Python module that simplifies parallelized computing for
those not familiar with Python's multiprocessing API. It includes
easy-to-use functions for deploying and managing computationally
expensive operations.

Simply said, it's a library that you can use to make your programs
faster!

Documentation
==============
Online documentation can be found here_.

You can find a Markdown version of the guide at GitHub_.

Bugs/Issues
============
DummyMP is currently in beta, so there's bound to be a few bugs.
Please report them to our `issues tracker`_.

.. _here: https://pythonhosted.org/dummymp/
.. _GitHub: https://github.com/alberthdev/dummymp/blob/master/docs/README.md
.. _issues tracker: https://github.com/alberthdev/dummymp/issues
"""

setup(
    name = 'dummymp',
    packages = ['dummymp'],
    version = '0.5b2',
    description = 'A multiprocessing library for dummies. (Library for easily running functions in parallel)',
    long_description = long_description,
    author='Albert Huang',
    author_email='alberth + a dot + dev + at + gmail + a dot + com',
    url='https://github.com/alberthdev/dummymp',
    download_url='https://github.com/alberthdev/dummymp/releases',
    license='Apache',
    keywords=[
        'multiprocessing', 'process', 'manager', 'task', 'manager',
        'taskmgr', 'psutil', 'parallel', 'parallelization', 'dummy',
        'queue',
        ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware',
        'Topic :: Utilities',
    ],
)
