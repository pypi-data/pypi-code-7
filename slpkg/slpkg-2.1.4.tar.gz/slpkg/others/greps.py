#!/usr/bin/python
# -*- coding: utf-8 -*-

# greps.py file is part of slpkg.

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

import os

from slpkg.toolbar import status
from slpkg.__metadata__ import lib_path
from slpkg.splitting import split_package
from slpkg.slack.slack_version import slack_ver

len_deps = 0


def repo_data(PACKAGES_TXT, step, repo, version):
    '''
    Grap data packages
    '''
    (name, location, size, unsize,
     rname, rlocation, rsize, runsize) = ([] for i in range(8))
    index, toolbar_width = 0, 700
    for line in PACKAGES_TXT.splitlines():
        index += 1
        toolbar_width = status(index, toolbar_width, step)
        if line.startswith("PACKAGE NAME"):
            name.append(line[15:].strip())
        if line.startswith("PACKAGE LOCATION"):
            location.append(line[21:].strip())
        if line.startswith("PACKAGE SIZE (compressed):  "):
            size.append(line[28:-2].strip())
        if line.startswith("PACKAGE SIZE (uncompressed):  "):
            unsize.append(line[30:-2].strip())
    if repo == "rlw":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = rlw_filter(name, location, size, unsize)
    elif repo == "alien":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = alien_filter(name, location, size, unsize, version)
    elif repo in ["slacky", "studio"]:
        rname, rlocation, rsize, runsize = name, location, size, unsize
    return [rname, rlocation, rsize, runsize]


def rlw_filter(name, location, size, unsize):
    '''
    Filter rlw repository data
    '''
    arch = os.uname()[4]
    if arch.startswith("i") and arch.endswith("86"):
        arch = "i486"
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        loc = l.split("/")
        if arch == loc[-1]:
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


def alien_filter(name, location, size, unsize, version):
    '''
    Filter alien repository data
    '''
    ver = slack_ver()
    if version == "current":
        ver = "current"
    path_pkg = "pkg"
    if os.uname()[4] == "x86_64":
        path_pkg = "pkg64"
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        if path_pkg == l.split("/")[-2] and ver == l.split("/")[-1]:
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


class Requires(object):

    def __init__(self, name, repo):
        self.name = name
        self.repo = repo
        lib = lib_path + "slack_repo/PACKAGES.TXT"
        f = open(lib, "r")
        self.SLACK_PACKAGES_TXT = f.read()
        f.close()

    def get_deps(self):
        '''
        Grap package requirements from repositories
        '''
        if self.repo in ["alien", "slacky"]:
            lib = {
                'alien': lib_path + "alien_repo/PACKAGES.TXT",
                'slacky': lib_path + "slacky_repo/PACKAGES.TXT"
            }
            f = open(lib[self.repo], "r")
            PACKAGES_TXT = f.read()
            f.close()
            for line in PACKAGES_TXT.splitlines():
                if line.startswith("PACKAGE NAME: "):
                    pkg = line[14:].strip()
                    pkg_name = split_package(pkg)[0]
                if line.startswith("PACKAGE REQUIRED: "):
                    if pkg_name == self.name:
                        if line[17:].strip():
                            if self.repo == "slacky":
                                return self.slacky_req_fix(line)

                            else:
                                return line[18:].strip().split(",")
        elif self.repo == "rlw":
            # Robby's repository dependencies as shown in the central page
            # http://rlworkman.net/pkgs/
            dependencies = {
                "abiword": "wv",
                "claws-mail": "libetpan bogofilter html2ps",
                "inkscape": "gtkmm atkmm pangomm cairomm mm-common libsigc++ "
                            "libwpg lxml gsl numpy BeautifulSoup",
                "texlive": "libsigsegv texi2html",
                "xfburn": "libburn libisofs"
            }
            if self.name in dependencies.keys():
                return dependencies[self.name].split()
            else:
                return ""

    def slacky_req_fix(self, line):
        '''
        Fix slacky requirements because many dependencies splitting
        with ',' and others with '|'
        '''
        slacky_deps = []
        for dep in line[18:].strip().split(","):
            dep = dep.split("|")
            if len(dep) > 1:
                for d in dep:
                    slacky_deps.append(d.split()[0])
            dep = "".join(dep)
            slacky_deps.append(dep.split()[0])
        slacky_deps = self.remove_slack_deps(slacky_deps)
        return slacky_deps

    def remove_slack_deps(self, dependencies):
        '''
        Because the repository slacky mentioned packages and dependencies
        that exist in the distribution Slackware, this feature is intended
        to remove them and return only those needed.
        '''
        global len_deps
        len_deps += len(dependencies)
        name, slacky_deps = [], []
        index, toolbar_width, step = 0, 700, (len_deps * 500)
        for line in self.SLACK_PACKAGES_TXT.splitlines():
            index += 1
            toolbar_width = status(index, toolbar_width, step)
            if line.startswith("PACKAGE NAME:"):
                name.append("-".join(line[15:].split("-")[:-3]))
        for deps in dependencies:
            if deps not in name:
                slacky_deps.append(deps)
        return slacky_deps
