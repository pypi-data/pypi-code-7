# coding=utf-8
import os
import sys
from setuptools import setup, find_packages


NAME = 'rms2dfinder'
VERSION = '0.1.2'


def read(filename):
    BASE_DIR = os.path.dirname(__file__)
    with open(os.path.join(BASE_DIR, filename)) as fi:
        return fi.read()


def readlist(filename):
    rows = read(filename).split("\n")
    rows = [x.strip() for x in rows if x.strip()]
    return list(rows)


extras = {}
if sys.version_info >= (3,):
    extras['use_2to3'] = True


setup(
    name=NAME,
    version=VERSION,
    description=(
        "A helper utility to find minimum mean RMSd structures of "
        "clusters found in rms2d plot."
    ),
    long_description=read('README.rst'),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
    keywords = 'utility Amber rms2d molecular dynamics',
    author = 'Alisue',
    author_email = 'lambdalisue@hashnote.net',
    url = 'https://github.com/lambdalisue/%s' % NAME,
    download_url = 'https://github.com/lambdalisue/%s/tarball/master' % NAME,
    license = 'MIT',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    package_data = {
        '': [
            'LICENSE', 'README.rst',
            'requirements.txt',
        ]
    },
    zip_safe=True,
    install_requires=readlist('requirements.txt'),
    entry_points={
        'console_scripts': [
            'rms2dfinder = rms2dfinder.rms2dfinder:main',
        ],
    },
    **extras
)
