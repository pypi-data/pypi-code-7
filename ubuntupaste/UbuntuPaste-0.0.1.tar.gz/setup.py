#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Setup.py
#
# Author: Kevin Hu

from setuptools import setup

setup(name = "UbuntuPaste",
      version = "0.0.1",
      description = "A gadget to paste file to UbuntuPaste from cli",
      author = "Kevin Hu",
      author_email = "hxy9243@gmail.com",
      keywords = "ubuntu pastebin",
      url = "https://github.com/hxy9243/UbuntuPaste",
      packages = ["ubuntupaste"],
      package_dir = {"ubuntupaste": "ubuntupaste"},
      scripts = ["bin/up"],
      platforms = ["Linux"],
      classifiers = ["Development Status :: 3 - Alpha",
                     "Topic :: Utilities",
                     "Environment :: Console",
                     "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)"
                    ]
)
