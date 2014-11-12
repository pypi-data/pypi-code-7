from sys import argv

from setuptools import setup

version = '0.0.2'

install_requires = []
if 'develop' in argv:
    install_requires += ['pytest>=2.6', 'pytz']

packages = ['qython', 'qython.datetime']

setup(name='qython', version=version, packages=packages, license='BSD',
      description='A missing library for python.',
      url='https://github.com/vamf12/qython',
      install_requires=install_requires)
