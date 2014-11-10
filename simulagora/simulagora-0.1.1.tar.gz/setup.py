#!/usr/bin/env python
# pylint: disable=W0142,W0403,W0404,W0613,W0622,W0622,W0704,R0904,C0103,E0611
#
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# Simulagora-client is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this software.  If not, see <http://www.gnu.org/licenses/>.

"""Generic Setup script, takes package info from __pkginfo__.py file
"""
__docformat__ = "restructuredtext en"

import os
import sys
import shutil
from os.path import isdir, exists, join

try:
    if os.environ.get('NO_SETUPTOOLS'):
        raise ImportError() # do as there is no setuptools
    from setuptools import setup
    from setuptools.command import install_lib
    USE_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    from distutils.command import install_lib
    USE_SETUPTOOLS = False
from distutils.command import install_data

# import required features
from __pkginfo__ import modname, version, license, description, web, \
     author, author_email, classifiers

if exists('README'):
    long_description = file('README').read()
else:
    long_description = ''

# import optional features
import __pkginfo__
if USE_SETUPTOOLS:
    requires = {}
    for entry in ("__depends__",): # "__recommends__"):
        requires.update(getattr(__pkginfo__, entry, {}))
    install_requires = [("%s %s" % (d, v and v or "")).strip()
                       for d, v in requires.iteritems()]
else:
    install_requires = []

distname = getattr(__pkginfo__, 'distname', modname)
scripts = getattr(__pkginfo__, 'scripts', ())
data_files = getattr(__pkginfo__, 'data_files', None)
ext_modules = getattr(__pkginfo__, 'ext_modules', None)
dependency_links = getattr(__pkginfo__, 'dependency_links', ())

BASE_BLACKLIST = ('CVS', '.svn', '.hg', 'debian', 'dist', 'build')
IGNORED_EXTENSIONS = ('.pyc', '.pyo', '.elc', '~')


def ensure_scripts(linux_scripts):
    """
    Creates the proper script names required for each platform
    (taken from 4Suite)
    """
    from distutils import util
    if util.get_platform()[:3] == 'win':
        scripts_ = [script + '.bat' for script in linux_scripts]
    else:
        scripts_ = linux_scripts
    return scripts_


# re-enable copying data files in sys.prefix
old_install_data = install_data.install_data
if USE_SETUPTOOLS:
    # overwrite InstallData to use sys.prefix instead of the egg directory
    class MyInstallData(old_install_data):
        """A class that manages data files installation"""
        def run(self):
            _old_install_dir = self.install_dir
            if self.install_dir.endswith('egg'):
                self.install_dir = sys.prefix
            old_install_data.run(self)
            self.install_dir = _old_install_dir
    try:
        import setuptools.command.easy_install # only if easy_install available
        # monkey patch: Crack SandboxViolation verification
        from setuptools.sandbox import DirectorySandbox as DS
        old_ok = DS._ok
        def _ok(self, path):
            """Return True if ``path`` can be written during installation."""
            out = old_ok(self, path) # here for side effect from setuptools
            realpath = os.path.normcase(os.path.realpath(path))
            allowed_path = os.path.normcase(sys.prefix)
            if realpath.startswith(allowed_path):
                out = True
            return out
        DS._ok = _ok
    except ImportError:
        pass

def install(**kwargs):
    """setup entry point"""
    if USE_SETUPTOOLS:
        if '--force-manifest' in sys.argv:
            sys.argv.remove('--force-manifest')
    # install-layout option was introduced in 2.5.3-1~exp1
    elif sys.version_info < (2, 5, 4) and '--install-layout=deb' in sys.argv:
        sys.argv.remove('--install-layout=deb')
    kwargs['package_dir'] = {modname : 'simulagora'}
    kwargs['packages'] = [modname]
    if USE_SETUPTOOLS:
        kwargs['install_requires'] = install_requires
        kwargs['dependency_links'] = dependency_links
        kwargs['zip_safe'] = False

    return setup(name = distname,
                 version = version,
                 license = license,
                 description = description,
                 long_description = long_description,
                 author = author,
                 author_email = author_email,
                 url = web,
                 scripts = ensure_scripts(scripts),
                 data_files = data_files,
                 ext_modules = ext_modules,
                 classifiers = classifiers,
                 **kwargs
                 )

if __name__ == '__main__' :
    install()
