#!/usr/bin/env python
from setuptools import setup

setup(
    name="mommy_spatial_generators",
    version='0.0.1',
    url='https://github.com/PSU-OIT-ARC/mommy_spatial_generators',
    author='Matt Johnson',
    author_email='mdj2@pdx.edu',
    description="GeoDjango generators for model_mommy",
    packages=['spatial_generators'],
    zip_safe=False,
    install_requires=['model_mommy'],
    classifiers=[
        'Framework :: Django',
    ],
    include_package_data=True,
)
