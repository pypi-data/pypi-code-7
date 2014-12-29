from setuptools import setup, find_packages
from codecs import open
from os import path

import malibu

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding = 'utf-8') as f:
    long_description = f.read()

setup(
    name = 'malibu',
    version = malibu.__version__,
    description = "maiome's library of utilities",
    long_description = long_description,

    url = "http://phabricator.maio.me/diffusion/MBU",
    author = "maiome development",
    author_email = "sean.johnson@maio.me",
    
    license = "Unlicense",
    
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: Public Domain",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords = 'malibu development database configuration',
    packages = ['malibu']
)
