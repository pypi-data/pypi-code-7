# coding=utf-8
from distutils.core import setup
from setuptools import setup, find_packages

"""
A set of helper Python modules used by Internet Services LLC.
"""

setup(
	name='ispl',
	version='0.0.1',
	url='https://github.com/inetss/ispl',
	license='BSD',
	author='Ilya Semenov',
	author_email='semenov@inetss.com',
	description='Internet Services Python Library',
	long_description=__doc__,
	packages=find_packages(),
        include_package_data=True,
	zip_safe=False,
	platforms='any',
	install_requires=[],
	classifiers=[
		# As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Internet',
		'Topic :: Scientific/Engineering',
	]
)
