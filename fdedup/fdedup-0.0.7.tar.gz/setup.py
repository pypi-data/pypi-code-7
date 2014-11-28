# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

from setuptools.command.test import test as test_command
import sys

class Tox(test_command):

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        test_command.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        test_command.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)

setup(
    name='fdedup',
    packages=['fdedup'],
    version='0.0.7',
    description='Command line tool to find file duplicates.',
    author='Alexander Krasnukhin, Alexey Ulyanov',
    author_email='the.malkom@gmail.com, sibuser.nsk@gmail.com',
    url='https://github.com/themalkolm/fdedup',
    download_url='https://github.com/themalkolm/fdedup',
    keywords=['files', 'duplicates'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7'
    ],
    entry_points={
        'console_scripts': [
            'fdedup = fdedup.main:main'
        ]
    },
    tests_require=['tox'],
    cmdclass={'test': Tox}
)
