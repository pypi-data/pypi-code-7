#!/usr/bin/env python
from distutils.core import setup
readme = open('README.rst').read()

from pip.req import parse_requirements
install_reqs = parse_requirements('requirements.txt')
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='django-spreadsheet-reports',
    version='0.01.1',
    author_email='gattster@gmail.com',
    author='Philip Gatt',
    description="Automates the tasks of producing simple reports from Django models.",
    long_description=readme,
    url='http://github.com/defcube/django-spreadsheet-reports',
    packages=['django_spreadsheet_reports'],
    include_package_data=True,
    data_files=[('', ['README.rst', 'requirements.txt'])],
    install_requires=reqs
)