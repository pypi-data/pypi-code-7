#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os.path
from setuptools import setup
from distutils.core import Extension
from distutils.command.build_ext import build_ext
from subprocess import check_call
from mail2news import VERSION, DESC


class Build_WLP_ext(build_ext):
    def run(self):
        self.make_file(
            'wlp/commands.y', 'wlp/commands.tab.c', check_call,
            # Yes, the following line contains list-in-list-in-tuple, and
            # that's how it should be.
            # otherwise, subsequent calls down the stack unwind the list and
            # check_call won't get it.
            ([['yacc', '-d', '-o', 'wlp/commands.tab.c', 'wlp/commands.y']]),
            'Generating lexer')
        self.make_file(
            'wlp/commands.l', 'wlp/lex.yy.c', check_call,
            ([['lex', '-o', 'wlp/lex.yy.c', 'wlp/commands.l']]),
            'Generating parser')
        build_ext.run(self)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# see https://github.com/Turbo87/py-xcsoar/blob/master/setup.py
wlp_module = Extension('wlp',
                       sources=['wlp/wlp.c',
                                'wlp/structs.c',
                                'wlp/commands.tab.c',
                                'wlp/lex.yy.c'])


setup(name='pygn',
      version=VERSION,  # the current Debian version is 0.9.8
      author="Cosimo Alfarano, Matej Cepl",
      author_email="kalfa@debian.org, mcepl@cepl.eu",
      description=DESC,
      long_description=read('README'),
      url='https://gitlab.com/mcepl/pyg',
      py_modules=['mail2news', 'news2mail', 'setup', 'whitelist'],
      ext_modules=[wlp_module],
      test_suite="test",
      scripts=['pygm2n', 'pygn2m'],
      cmdclass={
          'build_ext': Build_WLP_ext
      },
      # TODO package actually requires lex and yacc port, but not sure
      # how to say it here
      requires=[],
      license="GPLv3",
      keywords=["nntp", "email", "gateway"],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: System Administrators',
          'Topic :: Utilities',
          'Topic :: Communications :: Usenet News',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU Affero General Public License v3'
      ]
      )
