
from setuptools import setup, find_packages

setup(
    name = "trie_mod",
    version = "1.0",
    packages = find_packages(),
    py_modules = ['trie_mod'],

    # metadata for upload to PyPI
    author = "Daniel Richard Stromberg",
    author_email = "strombrg@gmail.com",
    description='Pure Python trie nodule',
    long_description='''
A pure python trie class is provided.  It is
thoroughly unit tested, passes pylint, and is known
to run on CPython 2.[567], CPython 3.[01234], Pypy 2.4.0, Pypy3 2.4.0 and
Jython 2.7b3.

This trie looks like a dictionary that's always
sorted by key.  It's well suited to storing large, natural-language dictionaries.

Note that although the iteration API is lazy, the implementation
is still eager.

It gives constant time access to a potentially-large collection
of strings.
''',
    license = "Apache v2",
    keywords = "Trie, dictionary-like, sorted dictionary",
    url='http://stromberg.dnsalias.org/~strombrg/trie-mod/',
    platforms='Cross platform',
    classifiers=[
         "Development Status :: 5 - Production/Stable",
         "Intended Audience :: Developers",
         "Programming Language :: Python :: 2",
         "Programming Language :: Python :: 3",
         ],
)

