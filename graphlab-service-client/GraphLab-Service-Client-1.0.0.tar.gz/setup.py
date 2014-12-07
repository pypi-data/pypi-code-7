#!/usr/bin/env python

import os
import sys
import glob
import subprocess
import shutil
from setuptools import setup, find_packages

VERSION="1.0.0"

if __name__ == '__main__':
    setup(
        name="GraphLab-Service-Client",
        version=VERSION,
        author='GraphLab, Inc.',
        author_email='contact@graphlab.com',
        packages=find_packages(),
        url='http://graphlab.com',
        license='LICENSE.txt',
        description='GraphLab Service Client makes it easy to make REST API calls to GraphLab Predictive Services',
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: Financial and Insurance Industry",
            "Intended Audience :: Information Technology",
            "Intended Audience :: Other Audience",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License", 
            "Natural Language :: English",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
            "Operating System :: POSIX :: BSD",
            "Operating System :: Unix",
            "Programming Language :: Python :: 2.7",
            "Topic :: Scientific/Engineering",
            "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
            "Topic :: Scientific/Engineering :: Information Analysis",
        ],
        install_requires=[
            "requests == 2.3.0",
        ],
    )
