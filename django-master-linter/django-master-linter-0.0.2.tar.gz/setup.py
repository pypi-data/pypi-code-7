# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-master-linter',
    version=open('djangomaster_linter/version.txt').read().strip(),
    author=u'Andre Farzat',
    author_email='andrefarzat@gmail.com',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/django-master-linter/',
    license='LICENSE',
    description='django master linter',
    long_description=open('README.md').read(),
    install_requires=open('requirements.txt').readlines(),
    include_package_data=True,
    zip_safe=False,
)
