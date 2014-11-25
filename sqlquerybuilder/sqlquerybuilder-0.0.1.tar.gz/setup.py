# encoding: utf-8
from distutils.core import setup
from setuptools import find_packages

setup(
    name='sqlquerybuilder',
    version='0.0.1',
    author='José Sánchez Moreno',
    author_email='jose@o2w.es',
    packages=find_packages(),
    license='LICENSE.txt',
    description=u'SQL Query Builder inspired on django ORM Syntax',
    long_description=open('readme.rst').read(),
    url='https://github.com/josesanch/sqlquerybuilder',
    install_requires=[
    ],
)
