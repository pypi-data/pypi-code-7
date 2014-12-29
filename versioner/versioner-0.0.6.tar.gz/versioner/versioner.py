#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 José Tomás Tocino <josetomas.tocino@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import re

FILENAME = 'VERSION'


class Versioner(object):
    file_format = re.compile(r"(\d+)\.(\d+)\.(\d+)")

    def __init__(self):
        self._major, self._minor, self._revision = 0, 0, 1

    def open(self, filename=FILENAME):
        try:
            with open(filename, 'rb') as f:
                file_contents = f.read().strip()

                if not Versioner.file_format.match(file_contents):
                    raise EnvironmentError

        except EnvironmentError:
            file_contents = "0.0.1"

        match = Versioner.file_format.match(file_contents)
        self._major, self._minor, self._revision = (int(x) for x in match.groups())

    def save(self, filename=FILENAME):
        with open(filename, 'wb') as f:
            f.write("{}.{}.{}".format(*self.get_version_components()))

    def get_version(self):
        return "{}.{}.{}".format(*self.get_version())

    def get_version_components(self):
        return self._major, self._minor, self._revision

    def set_major(self, major):
        assert isinstance(major, int)
        self._major = major

    def set_minor(self, minor):
        assert isinstance(minor, int)
        self._minor = minor

    def set_revision(self, revision):
        assert isinstance(revision, int)
        self._revision = revision

    def set_version(self, major, minor, revision):
        self.set_major(major)
        self.set_minor(minor)
        self.set_revision(revision)


def main():
    v = Versioner()
    v.open()

    major, minor, revision = v.get_version_components()

    arguments = sys.argv[1:]

    for argument in arguments:
        if argument == "+major":
            major += 1
        elif argument == "-major":
            major -= 1 if major > 0 else 0
        elif argument.startswith("major="):
            match = re.match(r"major=(\d+)", argument)
            if match:
                major = int(match.group(1))

        elif argument == "+minor":
            minor += 1
        elif argument == "-minor":
            minor -= 1 if minor > 0 else 0
        elif argument.startswith("minor="):
            match = re.match(r"minor=(\d+)", argument)
            if match:
                minor = int(match.group(1))

        elif argument == "+revision":
            revision += 1
        elif argument == "-revision":
            revision -= 1 if revision > 0 else 0
        elif argument.startswith("revision="):
            match = re.match(r"revision=(\d+)", argument)
            if match:
                revision = int(match.group(1))

    print "{}.{}.{}".format(major, minor, revision)

    v.set_version(major, minor, revision)
    v.save()

if __name__ == '__main__':
    main()