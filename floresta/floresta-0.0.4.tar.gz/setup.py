# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# <floresta - >

import ast
import os
import re
from setuptools import setup, find_packages


class VersionFinder(ast.NodeVisitor):

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        if node.targets[0].id == '__version__':
            self.version = node.value.s


def read_version():
    """Read version from floresta/version.py without loading any files"""
    finder = VersionFinder()
    finder.visit(ast.parse(local_file('floresta', 'version.py')))
    return finder.version


def parse_requirements(path):
    """Rudimentary parser for the `requirements.txt` file

    We just want to separate regular packages from links to pass them to the
    `install_requires` and `dependency_links` params of the `setup()`
    function properly.
    """
    try:
        requirements = map(str.strip, local_file(path).splitlines())
    except IOError:
        raise RuntimeError("Couldn't find the `%s' file :(" % path)

    links = []
    pkgs = []
    for req in requirements:
        if not req:
            continue
        if 'http:' in req or 'https:' in req:
            links.append(req)
            name, version = re.findall("\#egg=([^\-]+)-(.+$)", req)[0]
            pkgs.append('{0}=={1}'.format(name, version))
        else:
            pkgs.append(req)

    return pkgs, links


local_file = lambda *f: \
    open(os.path.join(os.path.dirname(__file__), *f)).read()


install_requires, dependency_links = \
    parse_requirements('requirements.txt')

print "\033[1;37m=============="
print "VERSION", read_version()
print "==============\033[0m"


setup(name='floresta',
      version=read_version(),
      description='Amazon VPC deployment tool',
      long_description=local_file('README.md'),
      author='Gabriel Falcao',
      author_email='gabriel@nacaolivre.org',
      url='http://github.com/gabrielfalcao/floresta',
      packages=find_packages(exclude=['*tests*']),
      tests_require=parse_requirements('requirements.txt'),
      install_requires=install_requires,
      dependency_links=dependency_links,
      license='MIT',
      entry_points={
          'console_scripts': [
              'floresta = floresta.cli:run_cli',
          ]
      },
      test_suite='nose.collector')
