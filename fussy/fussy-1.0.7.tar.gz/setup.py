#! /usr/bin/env python
from setuptools import setup, find_packages
import os

def get_version():
    filename = os.path.join('fussy','version.py') 
    if not os.path.exists(filename):
        return '1.0.0'
    for line in open(filename):
        if line.startswith( '__version__' ):
            return line.split('=')[1].strip().strip('"').strip("'")
    raise RuntimeError( "Unable to determine version" )

if __name__ == "__main__":
    setup(
        name='fussy',
        version=get_version(),
        description='Field-Upgradable Software Support',
        classifiers=[
            "Programming Language :: Python",
            "Operating System :: POSIX :: Linux",
            "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        ],
        license="LGPL",
        author='Mike C. Fletcher',
        author_email='mcfletch@vrplumber.com',
        url='http://www.vrplumber.com',
        keywords='firmware,field,upgrade,embedding',
        packages=find_packages(),
        include_package_data=True,
        # system-level requirements 
        # python2.6+
        # gpg
        # rsync
        # tar
        install_requires=[
            'distribute',
        ],
        entry_points = dict(
            console_scripts = [
                'fussy-install=fussy.install:main',
                'fussy-install-bytes=fussy.install:install_bytes_main', 
                'fussy-clean=fussy.install:clean_main',
                'fussy-unpack=fussy.unpack:main',
                'fussy-pack=fussy.pack:main',
                'fussy-south-rollback=fussy.southrollback:main',
                'fussy-link-tree=fussy.linktree:main',
                'fussy-log-server=fussy.jsonlogserver:main',
                'fussy-format-log=fussy.jsonlogserver:format_log_main',
                'json-format=fussy.jsonformat:main', 
            ],
        ),
    )
