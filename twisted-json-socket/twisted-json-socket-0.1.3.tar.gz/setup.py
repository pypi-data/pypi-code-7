#coding: utf-8
import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name="twisted-json-socket",
    version="0.1.3",
    author="Bo Kanstrup, Mads Sülau Jørgensen",
    author_email="bkh@konstellation.dk, msj@konstellation.dk",
    description=("Protocol for twisted json socket"),
    license="BSD",
    keywords="twsited json socket protocol",
    url="https://bitbucket.org/madssj/twisted-json-socket",
    packages=find_packages('src'),
    long_description=read('README'),
    package_dir={'': 'src'},
    install_requires=['twisted'],
    test_suite="tests",
)
