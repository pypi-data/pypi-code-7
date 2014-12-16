#!/usr/bin/python
# -*- coding: utf-8 -*-

# __metadata__.py file is part of slpkg.

# Copyright 2014 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Utility for easy management packages in Slackware

# https://github.com/dslackw/slpkg

# This program is free software: you can redistribute it and/or modify
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


__all__ = "slpkg"
__author__ = "dslackw"
__version_info__ = (2, 1, 4)
__version__ = "{0}.{1}.{2}".format(*__version_info__)
__license__ = "GNU General Public License v3 (GPLv3)"
__email__ = "d.zlatanidis@gmail.com"

# temponary path
tmp = "/tmp/"

# Default configuration values
slack_rel = "stable"
repositories = [
    'slack',
    'sbo',
    'rlw',
    'alien',
    'slacky',
    'studio'
]
build_path = "/tmp/slpkg/build/"
slpkg_tmp_packages = tmp + "slpkg/packages/"
slpkg_tmp_patches = tmp + "slpkg/patches/"
del_all = "on"
sbo_check_md5 = "on"
del_build = "off"
sbo_build_log = "on"
default_answer = "n"
remove_deps_answer = "n"
skip_unst = "n"
del_deps = "on"
use_colors = "on"

if os.path.isfile("/etc/slpkg/slpkg.conf"):
    f = open("/etc/slpkg/slpkg.conf", "r")
    conf = f.read()
    f.close()
    for line in conf.splitlines():
        line = line.lstrip()
        if line.startswith("VERSION"):
            slack_rel = line[8:].strip()
            if not slack_rel:
                slack_rel = "stable"
        if line.startswith("REPOSITORIES"):
            repositories = line[13:].strip().split(",")
        if line.startswith("BUILD"):
            build_path = line[6:].strip()
        if line.startswith("PACKAGES"):
            slpkg_tmp_packages = line[9:].strip()
        if line.startswith("PATCHES"):
            slpkg_tmp_patches = line[8:].strip()
        if line.startswith("DEL_ALL"):
            del_all = line[8:].strip()
        if line.startswith("DEL_BUILD"):
            del_build = line[10:].strip()
        if line.startswith("SBO_CHECK_MD5"):
            sbo_check_md5 = line[14:].strip()
        if line.startswith("SBO_BUILD_LOG"):
            sbo_build_log = line[14:].strip()
        if line.startswith("DEFAULT_ANSWER"):
            default_answer = line[15:].strip()
        if line.startswith("REMOVE_DEPS_ANSWER"):
            remove_deps_answer = line[19:].strip()
        if line.startswith("SKIP_UNST"):
            skip_unst = line[10:].strip()
        if line.startswith("DEL_DEPS"):
            del_deps = line[9:].strip()
        if line.startswith("USE_COLORS"):
            use_colors = line[11:].strip()

if use_colors == "on":
    color = {
        'RED': '\x1b[31m',
        'GREEN': '\x1b[32m',
        'YELLOW': '\x1b[33m',
        'CYAN': '\x1b[36m',
        'GREY': '\x1b[38;5;247m',
        'ENDC': '\x1b[0m'
    }
else:
    color = {
        'RED': '',
        'GREEN': '',
        'YELLOW': '',
        'CYAN': '',
        'GREY': '',
        'ENDC': ''
    }

# file spacer
sp = "-"

# current path
path = os.getcwd() + "/"

# library path
lib_path = "/var/lib/slpkg/"

# log path
log_path = "/var/log/slpkg/"

# packages log files path
pkg_path = "/var/log/packages/"

# computer architecture
arch = os.uname()[4]
