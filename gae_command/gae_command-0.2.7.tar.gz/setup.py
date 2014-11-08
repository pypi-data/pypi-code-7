import os, re
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

ver_re = r"""^\s*__version__\s*=\s*(?P<quot>['"])(?P<version>.*?)(?P=quot)\s*$"""
def package_version():
	verstr = "unknown"
	try:
		verstrline = read('gae_command/version.py')
	except EnvironmentError:
		pass # Okay, there is no version file.
	else:
		mo = re.search(ver_re, verstrline, re.MULTILINE)
		if mo:
			verstr = mo.group('version')
	return verstr

setup(
	name = "gae_command",
	version = package_version(),
	author = "Alex Bodnaru",
	author_email = "alexbodn@gmail.com",
	description = ("A tool to download and invoke gae commands."),
	license = "BSD",
	keywords = "gae",
	url = "http://packages.python.org/gae_command",
	long_description=read('README'),
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Topic :: Utilities",
		"Environment :: Console",
		"License :: OSI Approved :: BSD License",
	],
	install_requires=[
		'PasteScript',
	],
	entry_points="""
#	[paste.global_paster_command]
#	gae = gae_command.command:GAEGlobalCommand
#	gae-template = gae_command.template:GAETemplateCommand
#	gae-template-apply = gae_command.template:GAETemplateApplyCommand
	[paste.paster_create_template]
	gae = gae_command.template:GAETemplate
	gae-apply = gae_command.template:GAETemplateApply
	[console_scripts]
	gae = gae_command.command:run
	""",
	packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
	include_package_data=True,
)

