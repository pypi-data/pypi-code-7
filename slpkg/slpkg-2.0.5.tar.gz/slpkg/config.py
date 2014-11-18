#!/usr/bin/python
# -*- coding: utf-8 -*-

# config.py file is part of slpkg.

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
import subprocess

from colors import (
    CYAN,
    ENDC
)


def config_file():
    slpkg_conf = [
        "# Configuration file for slpkg\n",
        "\n",
        "# slpkg.conf file is part of slpkg.\n",
        "\n",
        "# Copyright 2014 Dimitris Zlatanidis <d.zlatanidis@gmail.com>\n",
        "# All rights reserved.\n",
        "\n",
        "# Utility for easy management packages in Slackware\n",
        "\n",
        "# https://github.com/dslackw/slpkg\n",
        "\n",
        "# Slpkg is free software: you can redistribute it and/or modify\n",
        "# it under the terms of the GNU General Public License as published " +
        "by\n",
        "# the Free Software Foundation, either version 3 of the License, or\n",
        "# (at your option) any later version.\n",
        "# This program is distributed in the hope that it will be useful,\n",
        "# but WITHOUT ANY WARRANTY; without even the implied warranty of\n",
        "# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n",
        "# GNU General Public License for more details.\n",
        "# You should have received a copy of the GNU General Public License\n",
        "# along with this program. If not, see <http://www.gnu.org/licenses/" +
        ">.\n",
        "\n",
        "# Slackware version 'stable' or 'current'.\n",
        "VERSION=stable\n",
        "\n",
        "# Build directory for repository slackbuilds.org. In this directory\n",
        "# downloaded sources and scripts for building.\n",
        "BUILD=/tmp/slpkg/build/\n",
        "\n",
        "# If SBO_CHECK_MD5 is 'on' the system will check all downloaded\n",
        "# sources from SBo repository.\n",
        "SBO_CHECK_MD5=on\n",
        "\n",
        "# Download directory for others repositories that use binaries files" +
        "\n",
        "# for installation.\n",
        "PACKAGES=/tmp/slpkg/packages/\n",
        "\n",
        "# Download directory for Slackware patches file.\n",
        "PATCHES=/tmp/slpkg/patches/\n",
        "\n",
        "# Delete all downloaded files if DEL_ALL is 'on'.\n",
        "DEL_ALL=on\n",
        "\n",
        "# Delete build directory after each process if DEL_BUILD is 'on'.\n",
        "DEL_BUILD=off\n",
        "\n",
        "# Keep build log file if SBO_BUILD_LOG is 'on'.\n",
        "SBO_BUILD_LOG=on\n"
    ]

    if not os.path.exists("/etc/slpkg"):
        os.mkdir("/etc/slpkg")
    if not os.path.isfile("/etc/slpkg/slpkg.conf"):
        with open("/etc/slpkg/slpkg.conf", "w") as conf:
            for line in slpkg_conf:
                conf.write(line)
            conf.close()
    return slpkg_conf


class Config(object):

    def __init__(self):
        self.config_file = "/etc/slpkg/slpkg.conf"

    def view(self):
        '''
        View slpkg config file
        '''
        print("")   # new line at start
        conf_args = [
            'VERSION',
            'BUILD',
            'SBO_CHECK_MD5',
            'PACKAGES',
            'PATCHES',
            'DEL_ALL',
            'DEL_BUILD',
            'SBO_BUILD_LOG'
        ]
        f = open(self.config_file, "r")
        read_conf = f.read()
        f.close()
        for line in read_conf.splitlines():
            if not line.startswith("#") and line.split("=")[0] in conf_args:
                print(line)
            else:
                print("{0}{1}{2}".format(CYAN, line, ENDC))
        print("")   # new line at end

    def edit(self, editor):
        '''
        Edit configuration file
        '''
        subprocess.call("{0} {1}".format(editor, self.config_file),
                        shell=True)
