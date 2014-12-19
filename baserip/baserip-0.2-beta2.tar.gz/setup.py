#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import baserip

readme = open('README.txt')
setup(
        name=baserip.__name,
        version=baserip.__version,
        description=baserip.__description,
        long_description=''.join(readme.readlines()),
        author="Geoff Clements",
        author_email="geoff@electron.me.uk",
        url="http://www.electron.me.uk",
        classifiers=[
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Environment :: X11 Applications",
            "Environment :: X11 Applications :: Qt",
            "Intended Audience :: End Users/Desktop",
            "Natural Language :: English",
            "Operating System :: POSIX :: Linux",
            "Topic :: Multimedia :: Video",
            "Topic :: Multimedia :: Video :: Conversion"
        ],
        install_requires=('pyudev >= 0.16'), 
        keywords="dvd transcoding video ripping",
        packages=find_packages(), 
#        package_dir = {'':'baserip'}, 
        include_package_data = True,
        exclude_package_data = {'': ["*.e4p"]}, 
        data_files=[('share', ['share/baserip.desktop', 'share/baserip.png'])], 
        entry_points = {'gui_scripts': ['baserip = baserip.baserip:run']}
)
