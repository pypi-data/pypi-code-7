import os
from setuptools import setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('README.rst') as readme:
    README = readme.read()

setup(
    name='diy-django',
    version='1.1.0',
    packages=['diydjango'],
    install_requires=['django'],
    description='diy-django',
    long_description=README,
    url='https://github.com/collinanderson/diy-django',
    author='Collin Anderson',
    author_email='cmawebsite@gmail.com',
    classifiers=[
        'Framework :: Django',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Programming Language :: Python :: 3',
    ],
    test_suite='diydjango',
)
