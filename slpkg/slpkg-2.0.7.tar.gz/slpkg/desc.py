#!/usr/bin/python
# -*- coding: utf-8 -*-

# desc.py file is part of slpkg.

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


from init import Initialization
from messages import pkg_not_found
from colors import (
    RED,
    GREEN,
    YELLOW,
    CYAN,
    GREY,
    ENDC
)
from __metadata__ import (
    pkg_path,
    lib_path,
    repositories
)

from pkg.find import find_package


class PkgDesc(object):

    def __init__(self, name, repo, color):
        self.name = name
        self.repo = repo
        self.color = color
        self.COLOR = ""
        self.lib = ""
        init_repos = {
            'sbo': Initialization().sbo,
            'slack': Initialization().slack,
            'rlw': Initialization().rlw,
            'alien': Initialization().alien,
            'slacky': Initialization().slacky
        }
        init_repos[self.repo]()
        color_text = {
            'red': RED,
            'green': GREEN,
            'yellow': YELLOW,
            'cyan': CYAN,
            'grey': GREY,
            '': ''
        }
        self.COLOR = color_text[self.color]
        if self.repo in repositories:
            repos = {
                'sbo': 'sbo_repo/SLACKBUILDS.TXT',
                'slack': 'slack_repo/PACKAGES.TXT',
                'rlw': 'rlw_repo/PACKAGES.TXT',
                'alien': 'alien_repo/PACKAGES.TXT',
                'slacky': 'slacky_repo/PACKAGES.TXT'
            }
            self.lib = lib_path + repos[self.repo]

    def view(self):
        end, n, count = ":", 1, 0
        find = "".join(find_package(self.name + '-', pkg_path))
        if self.repo == "sbo" and find.endswith("_SBo"):
            self.lib = pkg_path + find
        elif self.repo == "sbo" and not find:
            sbo_name = self.name
            self.name = "SLACKBUILD SHORT DESCRIPTION:  "
            end = sbo_name + " ("
            n = 0
        f = open(self.lib, "r")
        PACKAGES_TXT = f.read()
        f.close()
        print("")   # new line at start
        for line in PACKAGES_TXT.splitlines():
            if line.startswith(self.name + end):
                print("{0}{1}{2}".format(self.COLOR,
                                         line[len(self.name) + n:].strip(),
                      ENDC))
                count += 1
                if count == 11:
                    break
        if count == 0:
            if self.repo == "sbo":
                pkg_not_found("", sbo_name, "No matching", "\n")
            else:
                pkg_not_found("", self.name, "No matching", "\n")
        if self.repo == "sbo" and count > 0:
            print("")   # new line at end
