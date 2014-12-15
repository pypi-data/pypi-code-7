import os
from distutils.core import setup

VERSION = "0.2"

setup(
    name = "titration", 
    version = VERSION, 
    author = "Dieter Kadelka", 
    author_email = "DieterKadelka@aol.com",
    description = 'Computation and plotting of pH-values of acids, bases and mixtures.',
    requires = ['scipy.interpolate','scipy.optimize','matplotlib.pylab','multi_key_dict'],
    long_description = open('README.rst').read() if os.path.isfile('README.rst') else str(),
    py_modules = ["titration"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Teacher,Students',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    license='GPL',
    keywords='plotting, titration',
)
