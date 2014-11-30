#!/usr/bin/env python
from distutils.core import setup

readme = open('README.md').read()

setup(
    name='django-configurable-inclusion-tag',
    version='0.1.1',
    author_email='gattster@gmail.com',
    author='Philip Gatt',
    description="A smart template inclusion tag",
    long_description=readme,
    url='http://github.com/defcube/django_configurable_inclusion_tag/',
    py_modules=["django_configurable_inclusion_tag"],
    data_files=[('', ['README.md'])],
    )
