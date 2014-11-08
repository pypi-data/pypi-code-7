#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: bustta
# @Date:   2014-11-04 00:47:53
# @Last Modified by:   balicanta
# @Last Modified time: 2014-11-09 00:38:07

from distutils.core import setup

setup(
    name = 'newsParser',
    version = '0.0.6',
    packages = ['newsParser', 'newsParser.strategies'],
    description = 'Taiwan News Parser',
    author = 'lab317',
    author_email = 'balicanta@gmail.com',
    url = 'https://github.com/Lab-317/NewsParser',
    download_url = 'https://github.com/Lab-317/NewsParser/archive/v0.0.4.tar.gz',
    keywords = ['News', 'Parser', 'Taiwan'],
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Chinese (Traditional)"
    ],
)
