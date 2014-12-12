# Copyright (C) 2012-2014 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import sys
from setuptools import setup, find_packages

long_description = ""
try:
    try:
        script_dir = os.path.dirname(sys.argv[0])
        cmd = ['/usr/bin/make', 'readme']
        readme_file = 'README.txt'
        if script_dir not in (',', ''):
            cmd[1:1] = ['-C', script_dir]
            readme_file = os.path.join(script_dir, readme_file)
        with open('/dev/null', 'w') as null:
            ret = subprocess.call(cmd, stdout=null, stderr=null)
        if not ret:
            long_description = open(readme_file, 'rt').read()
    except Exception as err:
        sys.stderr.write('ERROR while reading README.txt: %s\n' % str(err))
    if not long_description:
        long_description = open('README.md', 'rt').read()
except IOError:
    pass

setup(
    name="openlmi-tools",
    description="OpenLMI (non)interactive shell and meta-command",
    long_description=long_description,
    version='0.10.4',
    license="GPLv2+",
    url="http://fedorahosted.org/openlmi/",
    author="Peter Hatina, Michal Minar",
    author_email="phatina@redhat.com, miminar@redhat.com",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Systems Administration",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "Environment :: Console",
    ],

    namespace_packages=["lmi", "lmi.scripts"],
    packages=(
            [ "lmi"
            , 'lmi.shell'
            , 'lmi.shell.compat'
            , 'lmi.scripts'
            , 'lmi.scripts._metacommand'
            , 'lmi.scripts.common'
            , 'lmi.scripts.common.command'
            , 'lmi.scripts.common.formatter'
            , 'lmi.scripts.common.versioncheck']),
    install_requires=["docopt >= 0.6", "openlmi", "pyparsing"],
    scripts=["lmishell"],

    entry_points={
        "console_scripts": [
            "lmi = lmi.scripts._metacommand:main"
            ],
        "lmi.scripts.cmd": [],
        },
    zip_safe=False,
)
