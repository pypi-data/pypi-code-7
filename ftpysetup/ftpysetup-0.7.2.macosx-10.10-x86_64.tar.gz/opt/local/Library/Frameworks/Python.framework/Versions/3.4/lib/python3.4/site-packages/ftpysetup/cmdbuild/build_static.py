#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#----------------------------------------------------------------------------
"""Enhance ``build_py`` to allow recursive directory globbing with ``**``."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.7.2'
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

__all__ = ['build_rglob']

import os
from glob import glob
from setuptools.command.build_py import build_py
from distutils.util import convert_path


class build_rglob(build_py):
    """Enhance ``build_py`` to allow recursive directory globbing with
    ``**``.
    """

    def find_data_files(self, package, src_dir):
        globs = (self.package_data.get('', [])
                 + self.package_data.get(package, []))

        globs = []
        for pattern in (self.package_data.get('', [])
                 + self.package_data.get(package, [])):
            if '**' in pattern:
                globs.extend(self.__expand_doublestar(src_dir, pattern))
            else:
                globs.append(pattern)

        files = self.manifest_files.get(package, [])[:]
        for pattern in globs:
            # Each pattern has to be converted to a platform-specific path
            gpath = os.path.join(src_dir, convert_path(pattern))
            files.extend(glob(gpath))
        return self.exclude_data_files(package, src_dir, files)

    def __expand_doublestar(self, src_dir, pattern):
        ret = []
        prefix, suffix = pattern.split(sep='**', maxsplit=1)
        suffix = suffix.lstrip(os.sep)
        rootdir = os.path.join(src_dir, prefix)
        for dirpath, dirnames, filenames in os.walk(rootdir):
            path = os.path.join(dirpath, suffix)
            ret.append(path)
        ret = [d.replace(src_dir + os.sep, '') for d in ret]
        return ret
