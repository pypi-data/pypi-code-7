import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
	README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name="django-commands",
	version="0.6",
	author="Paul Rutledge",
	author_email="paul.v.rutledge@gmail.com",
	description="A django app that provides a plugin type model for integrating the front and backend.",
	license="BSD",
	keywords="django command strategy plugin",
	url="https://github.com/RutledgePaulV/django-commands",
	include_package_data=True,
	long_description=README,
	packages=["commands"],
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
)