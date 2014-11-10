from setuptools import setup, find_packages
from distutils.core import setup
from codecs import open
from os import path

setup(
	name='kittenpaint',
	version='1.0',
	description='A paint program devided with a kitten stream, made for touch screens',
	url='https://github.com/HeadlessChild/pypaint-linux',
	author='Markus Lindberg',
	author_email='markus@tlindbeg.se',
	license='MIT',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
	],

	keywords='kitttens streaming paint',
	packages=find_packages(exclude=['distutils', 'distutils.command']),
	install_requires=['livestreamer'],
)
