
import os

from setuptools import setup, find_packages

os.system('make scapegoat_mod.py')

setup(
    name = "scapegoat_mod",
    version = "1.0",
    packages = find_packages(),
    py_modules = ['scapegoat_mod'],

    # metadata for upload to PyPI
    author = "Daniel Richard Stromberg",
    author_email = "strombrg@gmail.com",
    description='Pure Python scapegoat tree nodule',
    long_description='''
A pure python scapegoat splay tree class is provided.  It is
thoroughly unit tested, passes pylint, and is known
to run on CPython 2.x, CPython 3.x, Pypy 2.2 and
Jython 2.7b2.

This scapegoat tree looks like a dictionary that's always
sorted by key.  It also reorganizes itself on every
put.

Perhaps the most interesting thing about a scapegoat tree,
is it is balanced even for ordered keys, without any storage
overhead (unlike treaps and red-black trees).
''',
    license = "Apache v2",
    keywords = "Scapegoat tree, dictionary-like, sorted dictionary, cache",
    url='http://stromberg.dnsalias.org/~strombrg/scapegoat-tree/',
    platforms='Cross platform',
    classifiers=[
         "Development Status :: 5 - Production/Stable",
         "Intended Audience :: Developers",
         "Programming Language :: Python :: 2",
         "Programming Language :: Python :: 3",
         ],
)

