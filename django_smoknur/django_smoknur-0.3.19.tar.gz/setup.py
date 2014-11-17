# coding: utf-8

from setuptools import setup, find_packages
from os.path import join, dirname

import django_smoknur


setup(
    name='django_smoknur',
    version=django_smoknur.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    description='django-smoknur',
    author='Ilnur Gayfutdinov',
    author_email='ilnurgi87@gmail.com',
    url='https://bitbucket.org/ilnurgi/django-smoknur',
    zip_safe=False,
    include_package_data=True
)