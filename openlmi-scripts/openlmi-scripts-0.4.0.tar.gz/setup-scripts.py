#!/usr/bin/env python

# openlmi-scripts is deprecated egg. It shall be used just on distros with
# older openlmi-tools (older than 0.9.1) without LMI Meta-command.

import os
import subprocess
import sys
from setuptools import setup, find_packages

long_description = ''
try:
    try:
        script_dir = os.path.dirname(sys.argv[0])
        cmd = ['/usr/bin/make', 'readme', 'SOURCE=README-scripts.md']
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
        long_description = open('README-scripts.md', 'rt').read()
except IOError:
    pass

setup(
    name='openlmi-scripts',
    version='0.4.0',
    description='Client-side library and command-line client',
    long_description=long_description,
    author='Michal Minar',
    author_email='miminar@redhat.com',
    url="http://fedorahosted.org/openlmi/",
    platforms=['Any'],
    license="GPLv2+",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Systems Administration',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],

    namespace_packages=['lmi', 'lmi.scripts'],
    packages=[
        'lmi',
        'lmi.scripts',
        'lmi.scripts._metacommand',
        'lmi.scripts.common',
        'lmi.scripts.common.command',
        'lmi.scripts.common.formatter',
        'lmi.scripts.common.versioncheck'
    ],
    install_requires=[
        # version of tools >= 0.10.0 contains metacommand - this package
        # becomes redundant
        'openlmi-tools >= 0.9, < 0.10.0',
        'docopt >= 0.6',
        "pyparsing"],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'lmi = lmi.scripts._metacommand:main'
            ],
        'lmi.scripts.cmd': [],
        },
    )
