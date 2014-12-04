from setuptools import setup

version = '0.0.2'
name = 'gnsstime'
short_description = 'Extended datetime for the gnss analysis.'
long_description = """\
`gnsstime` is a extended datetime for the gnss analysis.

Requirements
------------
* Python 3.3 or later (not support 2.x)

Features
--------
* nothing

History
-------
0.0.2 (2014-12-04)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 3 - Alpha",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Scientific/Engineering",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    keywords=['gps', 'gnss', 'datetime'],
    author='Satoshi Kawamoto',
    author_email='satoshi.pes@gmail.com',
    url='None',
    license='PSL',
    #scripts = ['gnsstime.py']
    py_modules = ['gnsstime']
)


