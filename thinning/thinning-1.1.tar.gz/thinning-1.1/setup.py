# from distutils.core import setup, Extension
import numpy
import os.path
from setuptools import setup, Extension

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(here, 'README.txt')) as f:
	long_description = f.read()

setup(
	name='thinning',
	version='1.1',
	author = "Adrian Neumann",
	author_email = "adrian_neumann@gmx.de",
	url = "https://bitbucket.org/adrian_n/thinning",
	description = "C extension for thinning binary images.",
	ext_modules=[
		Extension(
			'thinning',
			['src/c_thinning.c'],
			include_dirs=[numpy.get_include(), os.path.join(numpy.get_include(),"numpy")]
		)
	],
	classifiers=[
		"Programming Language :: Python",
		"Programming Language :: Python :: 3", #I think
		"Programming Language :: Python :: 2",
		"Programming Language :: C",
		"License :: OSI Approved :: BSD License",
		"Topic :: Scientific/Engineering :: Image Recognition",
		"Intended Audience :: Developers",
		"Development Status :: 4 - Beta"
	],
	keywords=["image processing", "thinning", "guo hall"],
	long_description = long_description,
	install_requires=['numpy>=1.7'],
	license='BSD'
)