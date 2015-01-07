#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from distutils.core import setup
from io import open
from os import path


with open("README.md") as f:
    readme_content = f.read()

about = dict()
about_file = path.join("pyselection", "about.py")
with open(about_file) as f:
    about_lines = f.readlines()
    about_content = '\n'.join(about_lines[2:])
    exec(about_content, about)

setup(
    name = about['name'],
    version = about['version'],
    description = about['summary'],
    long_description = readme_content,
    author = about['author_name'],
    author_email = about['author_email'],
    url = about['package_url'],
    download_url = about['download_url'],
    packages = about['packages'],
    scripts = about['scripts'],
    classifiers = about['classifiers'],
    license = about['license'],
    keywords = about['keywords'],
    data_files= about['data_files']
)
