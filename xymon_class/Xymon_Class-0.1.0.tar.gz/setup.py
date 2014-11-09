
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Xymon_Class',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.1.0',

    description='A simple Class to manipulate Xymon test script',
    long_description=long_description,

    py_modules=['Xymon_Class'],
    
    # The project's main homepage.
    url='https://github.com/erikbeauvalot/Xymon_Class',

    # Author details
    author='Erik Beauvalot',
    author_email='erik@beauvalot.com',

  )
