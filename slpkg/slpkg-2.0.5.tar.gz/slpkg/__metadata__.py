#!/usr/bin/python
# -*- coding: utf-8 -*-

# __metadata__.py

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
import getpass

from config import config_file
from messages import s_user

__all__ = "slpkg"
__author__ = "dslackw"
__version_info__ = (2, 0, 5)
__version__ = "{0}.{1}.{2}".format(*__version_info__)
__license__ = "GNU General Public License v3 (GPLv3)"
__email__ = "d.zlatanidis@gmail.com"

s_user(getpass.getuser())

# temponary path
tmp = "/tmp/"

if not os.path.exists("/etc/slpkg/"):
    os.mkdir("/etc/slpkg/")

if not os.path.isfile("/etc/slpkg/slpkg.conf"):
    with open("/etc/slpkg/slpkg.conf", "w") as conf:
        for line in config_file():
            conf.write(line)
        conf.close()

f = open("/etc/slpkg/slpkg.conf", "r")
conf = f.read()
f.close()

# Default configuration values
slack_rel = "stable"
build_path = "/tmp/slpkg/build/"
slpkg_tmp_packages = tmp + "slpkg/packages/"
slpkg_tmp_patches = tmp + "slpkg/patches/"
del_all = "on"
sbo_check_md5 = "on"
del_build = "off"
sbo_build_log = "on"

for line in conf.splitlines():
    line = line.lstrip()
    if line.startswith("VERSION"):
        slack_rel = line[8:].strip()
        if not slack_rel:
            slack_rel = "stable"
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

# repositories
repositories = [
    "sbo",
    "slack",
    "rlw",
    "alien",
    "slacky"
]

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

# blacklist conf path
bls_path = "/etc/slpkg/"

# computer architecture
arch = os.uname()[4]
