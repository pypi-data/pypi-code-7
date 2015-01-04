#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""Update version information in a project."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.7'
__copyright__ = """Copyright (C) 2014 Lance Helsten"""
__docformat__ = "reStructuredText en"
__license__ = """
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

__all__ = ['UpdateVersion']

import sys
if sys.version_info < (3, 3):
    raise Exception("upvers requires Python 3.3 or higher.")
import os
import shutil
import errno
import re
import setuptools
from distutils.version import StrictVersion


VERS_RE = re.compile(r"""^(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<patch>\d+))?$""")


class UpdateVersion(setuptools.Command):
    description = "Modify project version by changing ``__version__`` tags."
    user_options = [
        ('set=', None, "Change version to given value."),
        ('major', None, "Move major number to next value set minor to 0."),
        ('minor', None, "Move minor number to next value remove patch."),
        ('patch', None, "Move patch number to next value."),
        ('alpha', None, "Make alpha or increment if already alpha."),
        ('beta', None, "Make beta or increment if already beta."),
        ('release', None, "Remove alpha or beta."),
    ]

    def initialize_options(self):
        self.set = None
        self.major = False
        self.minor = False
        self.patch = False
        self.alpha = False
        self.beta = False
        self.release = False

    def finalize_options(self):
        if self.set:
            try:
                self.set = StrictVersion(self.set)
            except ValueError as err:
                print("Error:", err, file=sys.stderr)
                sys.exit(errno.EINVAL)

            self.major = False
            self.minor = False
            self.patch = False
            self.alpha = False
            self.beta = False
            self.release = False
        else:
            self.major = bool(self.major)
            self.minor = bool(self.minor)
            self.patch = bool(self.patch)
            self.alpha = bool(self.alpha)
            self.beta = bool(self.beta)
            self.release = bool(self.release)

    def run(self):
        if self.set:
            newver = str(self.set)
        else:
            try:
                oldver = self.distribution.metadata.version
                oldver = StrictVersion(oldver)
            except ValueError as err:
                print("Error: setup.py", err, file=sys.stderr)
                sys.exit(errno.EINVAL)

            major, minor, patch = oldver.version
            pre = oldver.prerelease

            if self.alpha:
                if pre is None or pre[0] != 'a':
                    pre = ('a', 0)
                else:
                    pre = (pre[0], pre[1] + 1)
            elif self.beta:
                if pre is None or pre[0] != 'b':
                    pre = ('b', 0)
                else:
                    pre = (pre[0], pre[1] + 1)
            elif self.release:
                pre = None
            elif self.patch:
                patch = patch + 1
                pre = None
            elif self.minor:
                minor = minor + 1
                patch = 0
                pre = None
            elif self.major:
                major = major + 1
                minor = 0
                patch = 0
                pre = None
            else:
                return
            newver = StrictVersion()
            newver.version = (major, minor, patch)
            newver.prerelease = pre
            newver = str(newver)

        for dirpath, dirnames, filenames in os.walk(os.curdir):
            for filename in (f for f in filenames if os.path.splitext(f)[1] == '.py'):
                inpath = os.path.join(dirpath, filename)
                outpath = inpath + '.tmp'
                with open(inpath) as fin, open(outpath, 'w') as fout:
                    for line in fin:
                        if line.startswith("__version__"):
                            line = "__version__ = '{0}'\n".format(newver)
                        fout.write(line)
                shutil.copystat(inpath, outpath)
                os.replace(outpath, inpath)


