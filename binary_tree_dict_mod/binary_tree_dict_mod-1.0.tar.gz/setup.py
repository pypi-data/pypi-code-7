
import os

from setuptools import setup, find_packages

os.system('make binary_tree_dict_mod.py')

setup(
    name = "binary_tree_dict_mod",
    version = "1.0",
    packages = find_packages(),
    py_modules = ['binary_tree_dict_mod'],

    # metadata for upload to PyPI
    author = "Daniel Richard Stromberg",
    author_email = "strombrg@gmail.com",
    description='Pure Python binary tree (dictionary) module',
    long_description='''
A pure python binary tree class is provided.  It is
thoroughly unit tested, passes pylint, and is known
to run on CPython 2.x, CPython 3.x, Pypy 2.4.0, Pypy3 2.4.0 and
Jython 2.7b3.

This binary tree looks like a dictionary that's always
sorted by key.  It does not reorganize itself.

Although definitely a poor choice for pre-sorted keys, it's quite
good for pre-randomized keys.
''',
    license = "Apache v2",
    keywords = "binary tree, dictionary-like, sorted dictionary, cache",
    url='http://stromberg.dnsalias.org/~strombrg/binary-tree-dict/',
    platforms='Cross platform',
    classifiers=[
         "Development Status :: 5 - Production/Stable",
         "Intended Audience :: Developers",
         "Programming Language :: Python :: 2",
         "Programming Language :: Python :: 3",
         ],
)

