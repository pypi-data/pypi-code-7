from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
	import os

	return open(os.path.join(os.path.dirname(__file__), fname)).read()

def package_version():
	import os, re
	def read(fname):
		return open(os.path.join(os.path.dirname(__file__), fname)).read()

	ver_re = r"""^\s*release\s*:\s*(?P<quot>['"])(?P<version>.*?)(?P=quot)\s*$"""
	verstr = "unknown"
	try:
		verstrline = read('VERSION')
	except EnvironmentError:
		pass # Okay, there is no version file.
	else:
		mo = re.search(ver_re, verstrline, re.MULTILINE)
		if mo:
			verstr = mo.group('version')
	return verstr


setup(
	name = "google_appengine",
	version = package_version(),
	author = "Alex Bodnaru",
	author_email = "alexbodn@gmail.com",
	description = (
		"stub to allow running 'python setup.py develop' "
		"to make the underlying modules accessible "
		"in the current python environment"
		),
	license = read("LICENSE"),
	keywords = "gae sdk",
	url = "http://packages.python.org/gae_command",
	classifiers=[
		"Development Status :: 5 - Production",
	],
	install_requires=[
		'gae_command',
	],
	packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*', 'php']),
)

