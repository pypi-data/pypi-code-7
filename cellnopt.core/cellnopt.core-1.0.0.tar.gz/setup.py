# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 4869 2014-11-27 14:52:41Z cokelaer $" # for the SVN Id
import sys
import os
from setuptools import setup, find_packages
import glob


def get_datafiles(directory="share", match="*"):
    import fnmatch
    datafiles = []
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, match):
            matches.append(os.path.join(root, filename))
            this_filename = os.path.join(root, filename)
            datafiles.append((root, [this_filename]))
    return datafiles




_MAJOR               = 1
_MINOR               = 0
_MICRO               = 0
version              = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
release              = '%d.%d' % (_MAJOR, _MINOR)

metainfo = {
    'authors': {"main": ("Thomas Cokelaer", "cokelaer@ebi.ac.uk")},
    'version': version,
    'license' : 'GPL',
    'download_url' : ['http://pypi.python.org/pypi/cellnopt.core'],
    'url' : ["http://pythonhosted.org/cellnopt.core/"],
    'description': "Functions to manipulate networks and data related to signalling pathways." ,
    'platforms' : ['Linux', 'Unix', 'MacOsX', 'Windows'],
    'keywords' : ['SIF', "MIDAS", "SOP", "Kinexus", "CellNOpt", "CNOGraph"],
    'classifiers' : [
          'Development Status :: 7 - Inactive',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Physics']
    }

namespace = "cellnopt"
pkg_root_dir = 'src'
pkgs = [ pkg for pkg in find_packages(pkg_root_dir)]
top_pkgs = [pkg for pkg in pkgs if  len(pkg.split('.')) < 2]
packages = pkgs
package_dir = dict( [('',pkg_root_dir)] + [(namespace + "." + pkg, pkg_root_dir  + "/" + pkg) for pkg in top_pkgs] )


setup(
    name             = "cellnopt.core",
    version          = version,
    maintainer       = metainfo['authors']['main'][0],
    maintainer_email = metainfo['authors']['main'][1],
    author           = metainfo['authors']['main'][0],
    author_email     = metainfo['authors']['main'][1],
    long_description = open("README.txt").read(),
    keywords         = metainfo['keywords'],
    description      = metainfo['description'],
    license          = metainfo['license'],
    platforms        = metainfo['platforms'],
    url              = metainfo['url'],      
    download_url     = metainfo['download_url'],
    classifiers      = metainfo['classifiers'],

    # package installation
    package_dir = package_dir,
    #package_dir = { 'cellnopt.core' :   'src/core'},
    #packages = ['cellnopt.core', 'cellnopt.core.io'],
    packages = find_packages("src"),
    namespace_packages = [namespace],

    install_requires = ["easydev==0.7.4", "colormap==0.9.4", "numpy", "networkx", "pygraphviz",
        "pandas", "beautifulsoup4", "cellnopt.data"],
    # uncomment if you have share/data files
    data_files = get_datafiles("share", "*"),
    zip_safe = False
)
