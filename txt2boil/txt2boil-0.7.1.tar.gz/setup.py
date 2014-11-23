#!/usr/bin/python

# Copyright (C) 2014 Kieran Colford
#
# This file is part of txt2boil.
#
# txt2boil is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# txt2boil is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with txt2boil.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import *
from distutils.errors import DistutilsError
import os
import glob
from txt2boil import __version__ as version


class total_upload(Command):

    description = "upload all available binaries"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    commands = ['register',
                'sdist',
                'bdist_rpm',
                'bdist_msi', 'bdist_msi_fixed',
                'bdist_egg',
                'upload']

    def run(self):
        for c in self.commands:
            try:
                self.run_command(c)
            except DistutilsError:
                pass


with open(glob.glob('README.*')[0]) as f:
    long_description = '\n' + f.read()

setup(
    name='txt2boil', license='GPLv3+', version=version,

    description='Generate boilerplate from source code comments.',
    long_description=long_description,
    keywords=['boilerplate', 'comments'],

    author='Kieran Colford', author_email='colfordk@gmail.com',
    maintainer='Kieran Colford', maintainer_email='colfordk@gmail.com',

    url='https://github.com/kcolford/txt2boil',
    download_url='',            # TODO

    packages=find_packages(exclude=['test*', '*.test', '*.tests']),
    test_suite='test',
    entry_points={'console_scripts': ['txt2boil = txt2boil.main:main']},

    platforms=['Any'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 ' +
        'or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Code Generators',
    ],

    use_2to3=True,

    cmdclass={'total_upload': total_upload},

    setup_requires=['xdistutils'],
)
