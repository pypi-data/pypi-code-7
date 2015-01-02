# -*- coding: utf-8 -*-
import re
from setuptools import setup


REQUIRES = [
    'mercurial>=2.9',
]


def find_version(fname):
    '''Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    '''
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version("branchlog.py")


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='hg-branchlog',
    version=__version__,
    description='Modified hg graphlog command.',
    long_description='''
    branchlog is a modified form of the Mercurial graphlog command (hg log -G),
    which focuses on the merge structure between named branches, collapsing
    long sequences of commits in the same branch together.

    For more details (including pretty ascii graphics) see the project homepage
    at https://bitbucket.org/tikitu/branchlog.''',
    author='Tikitu de Jager',
    author_email='tikitu@logophile.org',
    url='https://bitbucket.org/tikitu/branchlog',
    install_requires=REQUIRES,
    license='GNU GPLv2 or any later version',
    zip_safe=False,
    keywords='branchlog',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    py_modules=['branchlog'],
    tests_require=[
        'nose',
        'mock',
    ],
    test_suite='nose.collector'
)