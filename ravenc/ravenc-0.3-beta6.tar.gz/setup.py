#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import ravenc

setup(
        name = ravenc.__name,
        version = ravenc.__version,
        description = ravenc.__description,
        long_description = ravenc.__readme,
        author = "Geoff Clements",
        author_email = "geoff@electron.me.uk",
        url = "http://www.electron.me.uk",
        classifiers = [
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Environment :: X11 Applications",
            "Environment :: X11 Applications :: Qt",
            "Intended Audience :: End Users/Desktop",
            "Natural Language :: English",
            "Operating System :: POSIX :: Linux",
            "Topic :: Multimedia :: Video",
            "Topic :: Multimedia :: Video :: Conversion"
        ],
        install_requires = ('pyudev >= 0.16'), 
        keywords = "dvd transcoding video ripping",
        packages = find_packages(), 
        include_package_data = True,
        exclude_package_data = {'': ["*.e4p"]}, 
        data_files = [
            ('/usr/share/applications', ['share/ravenc.desktop']),
            ('/usr/share/pixmaps', ['share/ravenc.xpm'])
            ], 
        entry_points = {'gui_scripts': ['ravenc = ravenc.ravenc:run']}
)
