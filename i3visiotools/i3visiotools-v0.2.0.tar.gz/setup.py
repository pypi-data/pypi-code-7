#from distutils.core import setup
import os

# Ensuring that Setuptools is install
import ez_setup
ez_setup.use_setuptools()

# Depending on the place in which the project is going to be upgraded
from setuptools import setup
try:
	from pypandoc import convert
	read_md = lambda f: convert(f, 'rst')
except ImportError:
	print("warning: pypandoc module not found, could not convert Markdown to RST")
	read_md = lambda f: open(f, 'r').read()

setup(	name="i3visiotools",
	version="v0.2.0",
	description="i3visiotools - Set of common tools shared by i3visio apps and libraries.",
	author="Felix Brezo and Yaiza Rubio",
	author_email="contacto@i3visio.com",
	url="http://github.com/i3visio/i3visiotools",
	license="COPYING",
	packages=[
		"i3visiotools", 
		"i3visiotools.wrappers", 
		"i3visiotools.apify", 
		"i3visiotools.darkfy",
		"i3visiotools.darkfy.lib",
		"i3visiotools.darkfy.lib.wrappers",
	],
#	scripts=[""],
	long_description=read_md("README.md"),
#	long_description=open('README.md').read(),
	install_requires=[
 	"mechanize",
	"Skype4Py",
	"argparse",
#	"pypandoc",
	],
)

