#!/usr/bin/python
# -*- coding: utf-8 -*-

# init.py file is part of slpkg.

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
import sys

from url_read import URL
from repositories import Repo
from file_size import FileSize
from __metadata__ import (
    log_path,
    lib_path,
    slack_rel,
    build_path,
    slpkg_tmp_packages,
    slpkg_tmp_patches
)

from slack.mirrors import mirrors
from slack.slack_version import slack_ver


class Initialization(object):

    def __init__(self):
        if not os.path.exists("/etc/slpkg/"):
            os.mkdir("/etc/slpkg/")
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        if not os.path.exists(lib_path):
            os.mkdir(lib_path)
        if not os.path.exists("/tmp/slpkg/"):
            os.mkdir("/tmp/slpkg/")
        if not os.path.exists(build_path):
            os.mkdir(build_path)
        if not os.path.exists(slpkg_tmp_packages):
            os.mkdir(slpkg_tmp_packages)
        if not os.path.exists(slpkg_tmp_patches):
            os.mkdir(slpkg_tmp_patches)

    def slack(self):
        '''
        Creating slack local libraries
        '''
        log = log_path + "slack/"
        lib = lib_path + "slack_repo/"
        lib_file = "PACKAGES.TXT"
        log_file = "ChangeLog.txt"
        version = slack_rel
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages = mirrors(lib_file, "", version)
        extra = mirrors(lib_file, "extra/", version)
        pasture = mirrors(lib_file, "pasture/", version)
        packages_txt = ("{0} {1} {2}".format(packages, extra, pasture))
        changelog_txt = mirrors(log_file, "", version)
        self.write(lib, lib_file, packages_txt)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt)

    def sbo(self):
        '''
        Creating sbo local library
        '''
        repo = Repo().sbo()
        log = log_path + "sbo/"
        lib = lib_path + "sbo_repo/"
        lib_file = "SLACKBUILDS.TXT"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}/{2}".format(repo, slack_ver(), lib_file)
        changelog_txt = "{0}/{1}/{2}".format(repo, slack_ver(), log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt)

    def rlw(self):
        '''
        Creating rlw local library
        '''
        repo = Repo().rlw()
        log = log_path + "rlw/"
        lib = lib_path + "rlw_repo/"
        lib_file = "PACKAGES.TXT"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}/{2}".format(repo, slack_ver(), lib_file)
        changelog_txt = "{0}{1}/{2}".format(repo, slack_ver(), log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt)

    def alien(self):
        '''
        Creating alien local library
        '''
        repo = Repo().alien()
        log = log_path + "alien/"
        lib = lib_path + "alien_repo/"
        lib_file = "PACKAGES.TXT"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}".format(repo, lib_file)
        changelog_txt = "{0}{1}".format(repo, log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt)

    def slacky(self):
        '''
        Creating alien local library
        '''
        ar = ""
        arch = os.uname()[4]
        repo = Repo().slacky()
        log = log_path + "slacky/"
        lib = lib_path + "slacky_repo/"
        lib_file = "PACKAGES.TXT"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        if arch == "x86_64":
            ar = "64"
        packages_txt = "{0}slackware{1}-{2}/{3}".format(repo, ar, slack_ver(),
                                                        lib_file)
        changelog_txt = "{0}slackware{1}-{2}/{3}".format(repo, ar, slack_ver(),
                                                         log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt)

    @staticmethod
    def write(path, files, file_url):
        '''
        Write files in /var/lib/slpkg/?_repo directory
        '''
        PACKAGES_TXT = ""
        if not os.path.isfile(path + files):
            print("\nslpkg ...initialization")
            sys.stdout.write(files + " read ...")
            sys.stdout.flush()
            for fu in file_url.split():
                PACKAGES_TXT += URL(fu).reading()
            sys.stdout.write("Done\n")
            with open("{0}{1}".format(path, files), "w") as f:
                f.write(PACKAGES_TXT)
                f.close()
                print("File {0} created in {1}".format(files, path))

    @staticmethod
    def remote(*args):
        '''
        args[0]=log, args[1]=log_file, arg[2]=changelog_txt
        args[3]=lib, args[4]=lib_file, arg[5]=packages_txt

        If the two files differ in size delete and replaced with new.
        We take the size of ChangeLog.txt from the server and locally
        '''
        PACKAGES_TXT = ""
        server = FileSize(args[2]).server()
        local = FileSize(args[0] + args[1]).local()
        if server != local:
            os.remove("{0}{1}".format(args[3], args[4]))
            os.remove("{0}{1}".format(args[0], args[1]))
            print("\nNEWS in " + args[1])
            print("slpkg ...initialization")
            sys.stdout.write("Files re-created ...")
            sys.stdout.flush()
            for fu in args[5].split():
                PACKAGES_TXT += URL(fu).reading()
            CHANGELOG_TXT = URL(args[2]).reading()
            with open("{0}{1}".format(args[3], args[4]), "w") as f:
                f.write(PACKAGES_TXT)
                f.close()
            with open("{0}{1}".format(args[0], args[1]), "w") as f:
                f.write(CHANGELOG_TXT)
                f.close()
            sys.stdout.write("Done\n")
