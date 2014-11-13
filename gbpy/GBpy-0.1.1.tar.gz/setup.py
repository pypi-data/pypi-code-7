import sys
import os
from setuptools import setup

main_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(main_dir, "GBpy"))
import GBpy
# del sys.path[0]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='GBpy',
    packages = ['GBpy','GBpy/csl_generators','GBpy/docs','GBpy/pkl_files'],
    include_package_data=True,
    version='0.1.1',
    author='Arash Dehghan Banadaki, Srikanth Patala',
    author_email='adehgha@ncsu.edu, spatala@ncsu.edu',
    description="GBpy is an opensource python package for calculating the geometric properties of interfaces in crystals.",
    long_description=read('PKG-INFO'),
    url='https://github.com/adehgha/GBpy',
    download_url = 'https://github.com/adehgha/GBpy/tarball/0.1.1',
    platforms='any',
    requires=['numpy', 'scipy','setuptools'],
    keywords = ['bicrystallography','interfaces','grain boundaries'],
    classifiers=['Development Status :: 2 - Pre-Alpha', 'License :: OSI Approved :: GNU General Public License (GPL)','Programming Language :: Python :: 2.6','Programming Language :: Python :: 2.7','Programming Language :: Python :: 3.0','Topic :: Scientific/Engineering :: Mathematics','Topic :: Scientific/Engineering :: Physics','Topic :: Software Development :: Libraries :: Python Modules','Topic :: Utilities'],
    license='License :: GNU-GPL',
)
