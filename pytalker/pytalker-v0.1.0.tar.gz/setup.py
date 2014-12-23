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

setup(	name="pytalker",
	version="v0.1.0",
	description="pytalker - Text-To-Speech code to wrap Google's TTS.",
	author="Felix Brezo and Yaiza Rubio",
	author_email="contacto@i3visio.com",
	url="http://github.com/i3visio/pytalker",
	license="COPYING",
	packages=["pytalker"],
	long_description=read_md("README.md"),
#	long_description=open('README.md').read(),
	install_requires=[
	"argparse",
#	"pypandoc",
	],
)

