#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils import setup
import os
import djbiblio

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Full list of classifiers can be found here:
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLS = \
 [ 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
 , 'Development Status :: 3 - Alpha'
 , 'Environment :: Web Environment'
 , 'Framework :: Django'
 , 'Intended Audience :: Science/Research'
 , 'Operating System :: OS Independent'
 , 'Programming Language :: Python'
 , 'Topic :: Text Processing :: Markup :: LaTeX'
 ]

REQS = [ 'django >= 1.6'
       , 'bibtexparser >= 0.6.0'
       ]

setup( name             = djbiblio.pkgname
     , description      = djbiblio.__description__
     , version          = djbiblio.__version__
     , author           = djbiblio.__author__
     , author_email     = djbiblio.__author_email__
     , license          = djbiblio.__license__
     , url              = djbiblio.__url__
     , long_description = read('README')
     , packages         = [ 'djbiblio' ]
     , classifiers      = CLS
     , install_requires = REQS
     )

