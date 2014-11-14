from distutils.core import setup
from setuptools import find_packages


setup(
    name='bobsleigh_seddonym',
    version='0.1.4',
    url='http://github.com/seddonym/bobsleigh-seddonym/',
    author='David Seddon',
    author_email='david@seddonym.me',
    description='Helpful Bobsleigh settings for my projects.',
    packages=find_packages(),
    include_package_data=True,
)
