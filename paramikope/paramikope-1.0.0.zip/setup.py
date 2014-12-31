from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='paramikope',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/development.html#single-sourcing-the-version
    version='1.0.0',

    description='A sample Python project',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/abyeipe88/paramiko-pexpect',

    # Author details
    author='Aby Alex',
    author_email='abyeipe88@gmail.com',

    # Choose your license
    license='MIT',

    # What does your project relate to?
    keywords='sample paramiko-pexpect',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['paramikope'],

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=['paramiko'],

)
