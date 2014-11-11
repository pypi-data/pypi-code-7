from setuptools import setup, Extension
from glob import glob
import os
import sys
from sqt import __version__

if sys.version_info < (2, 6):
	sys.stdout.write("At least Python 2.6 is required.\n")
	sys.exit(1)

try:
	from Cython.Build import cythonize
	USE_CYTHON = True
except ImportError:
	USE_CYTHON = False

ext = '.pyx' if USE_CYTHON else '.c'

extensions = [
	Extension('sqt._helpers', sources=['sqt/_helpers' + ext]),
	Extension('sqt._qualtrim', sources=['sqt/_qualtrim' + ext]),
]

if USE_CYTHON:
	extensions = cythonize(extensions)

setup(
	name = 'sqt',
	version = __version__,
	author = 'Marcel Martin',
	author_email = 'marcel.martin@scilifelab.se',
	url = 'https://bitbucket.org/marcelm/sqt',
	description = 'Command-line tools for the analysis of high-throughput sequencing data',
	license = 'MIT',
	packages = [ 'sqt', 'sqt.io', 'sqt.scripts' ],
	scripts = [ s for s in glob(os.path.join("bin", "sqt-*")) if not s.endswith('~') ],
	ext_modules = extensions,
	use_2to3 = True,
	test_suite = 'nose.collector',
	classifiers = [
		"Development Status :: 3 - Alpha",
		#Development Status :: 4 - Beta
		#Development Status :: 5 - Production/Stable
		"Environment :: Console",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Programming Language :: Python :: 2.6",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Topic :: Scientific/Engineering :: Bio-Informatics"
	]
)
