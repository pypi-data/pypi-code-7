#!/usr/bin/python
# -*- coding: utf-8 -*-

# search.py file is part of slpkg.

# Copyright 2014 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Utility for easy management packages in Slackware

# https://github.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys

from slpkg.blacklist import BlackList
from slpkg.__metadata__ import lib_path
from slpkg.splitting import split_package


def search_pkg(name, repo):
    '''
    Search if package exists in PACKAGES.TXT file
    and return the name.
    '''
    try:
        blacklist = BlackList().packages()
        repo_dir = {
            "rlw": "rlw_repo/PACKAGES.TXT",
            "alien": "alien_repo/PACKAGES.TXT",
            "slacky": "slacky_repo/PACKAGES.TXT",
            "studio": "studio_repo/PACKAGES.TXT"
        }
        with open(lib_path + repo_dir[repo], "r") as PACKAGES_TXT:
            for line in PACKAGES_TXT:
                if line.startswith("PACKAGE NAME:  "):
                    pkg_name = split_package(line[15:])[0].strip()
                    if name == pkg_name and name not in blacklist:
                        PACKAGES_TXT.close()
                        return pkg_name
    except KeyboardInterrupt:
        print("")   # new line at exit
        sys.exit(0)
