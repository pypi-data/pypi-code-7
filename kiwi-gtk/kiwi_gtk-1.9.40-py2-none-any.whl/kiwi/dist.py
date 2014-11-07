#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2005-2006 Async Open Source
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
# USA
#
# Author(s): Johan Dahlin <jdahlin@async.com.br>
#

"""Distutils extensions and utilities"""

import commands
from distutils.command.clean import clean
from distutils.command.install_data import install_data
from distutils.command.install_lib import install_lib
from distutils.dep_util import newer
from distutils.log import info, warn
from distutils.sysconfig import get_python_lib
import errno
from fnmatch import fnmatch
from shutil import copyfile
import os
import new
import subprocess
import sys

from setuptools import setup as DS_setup


class _VariableExtender:
    def __init__(self, distribution):
        install = distribution.get_command_obj('install')
        name = distribution.get_name()
        prefix = install.prefix
        if not prefix:
            prefix = sys.prefix

        # Remove trailing /
        if prefix[-1] == '/':
            prefix = prefix[:-1]
        self.prefix = prefix

        is_egg = 'bdist_egg' in distribution.commands
        if is_egg:
            self.datadir = name + '/data'
        else:
            self.datadir = os.path.join('share', name)

        if self.prefix == '/usr':
            self.sysconfdir = '/etc'
        else:
            self.sysconfdir = os.path.join('etc')

        pylib = get_python_lib()
        pylib = pylib.replace(sys.prefix + '/', '')
        self.libdir = os.path.dirname(os.path.dirname(pylib))

        self.version = distribution.get_version()

    def extend(self, string, relative=False):
        """
        Expand a variable.
        :param string: string to replace.
        :param relative: if True, assume the content of all variables
            to be relative to the prefix.
        """
        for name, var in [('sysconfdir', self.sysconfdir),
                          ('datadir', self.datadir),
                          ('prefix', self.prefix),
                          ('libdir', self.libdir),
                          ('version', self.version)]:
            if not relative and name not in ['prefix', 'version']:
                var = os.path.join(self.prefix, var)
            string = string.replace('$' + name, var)
        return string


class KiwiInstallLib(install_lib):
    # Overridable by subclass
    resources = {}
    global_resources = {}

    def _get_template(self):
        return os.path.join(self.install_dir,
                            self.distribution.get_name(),
                            '__installed__.py')

    def _get_revision(self):
        top_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        last_revision = os.path.join(top_dir, '.bzr', 'branch', 'last-revision')

        # If the file does not exist, we may be building a ppa recipe.
        # This happens because dpkg-source is run with -i -I, and that
        # causes .bzr files to be removed.
        if not os.path.exists(last_revision):
            last_revision = os.path.join(top_dir, 'last-revision')
            if not os.path.exists(last_revision):
                return 0

        try:
            fp = open(last_revision)
        except OSError, e:
            if e.errno != errno.ENOENT:
                raise
        else:
            return fp.read().split()[0]

    def generate_template(self):
        if 'bdist_wininst' in sys.argv or 'bdist_wheel' in sys.argv:
            prefix = 'sys.prefix'
        else:
            install = self.distribution.get_command_obj('install')
            # Use raw strings so UNC paths which has \\ works
            prefix = '%s' % install.prefix

        filename = self._get_template()
        self.mkpath(os.path.dirname(filename))
        revision = self._get_revision()
        fp = open(filename, 'w')
        # Frozen assumes that prefix is .. relative to library.zip
        fp.write("""# Generated by setup.py do not modify
import os
import sys
prefix = %r
if hasattr(sys, 'frozen'):
    pos = __file__.find('library.zip')
    prefix = os.path.dirname(__file__[:pos-1])
elif not os.path.exists(prefix):
    prefix = sys.prefix
revision = %r
""" % (prefix, revision))
        self._write_dictionary(fp, 'resources', self.resources)
        self._write_dictionary(fp, 'global_resources', self.global_resources)
        fp.close()

        return filename

    def _write_dictionary(self, fp, name, dictionary):
        fp.write('%s = {}\n' % name)
        for key, value in dictionary.items():
            value = value.replace('/', os.sep)
            value = self.varext.extend(value)
            value = value.replace(self.varext.prefix, '$prefix')
            parts = []
            for part in value.split(os.sep):
                if part == "":
                    part = os.sep
                if part == '$prefix':
                    part = 'prefix'
                else:
                    part = '"%s"' % part
                parts.append(part)
            fp.write("%s['%s'] = %s\n" % (
                name, key, 'os.path.join(%s)' % ', '.join(parts)))

    def get_outputs(self):
        filename = self._get_template()
        files = [filename] + self._bytecode_filenames([filename])

        return install_lib.get_outputs(self) + files

    def install(self):
        self.varext = _VariableExtender(self.distribution)
        return install_lib.install(self) + [self.generate_template()]

# Backwards compat
TemplateInstallLib = KiwiInstallLib


class KiwiInstallData(install_data):
    def run(self):
        self.varext = _VariableExtender(self.distribution)

        # Extend variables in all data files
        data_files = []
        for target, files in self.data_files[:]:
            data_files.append((self.varext.extend(target, True), files))
        self.data_files = data_files
        return install_data.run(self)


# This is so ulgy, but its the only way I found out to include bzr
# last-revision when building a source with debuild -S -i -I.
# XXX FIXME: Figure out a better way to do this.
class KiwiClean(clean):
    def run(self):
        retval = clean.run(self)
        top_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        dest = os.path.join(top_dir, 'last-revision')
        git_src = os.path.join(top_dir, '.git', 'HEAD')
        bzr_src = os.path.join(top_dir, '.bzr', 'branch', 'last-revision')
        if os.path.exists(git_src):
            status, output = commands.getstatusoutput(
                'git rev-parse --short HEAD')
            if status == 0:
                info("Writing git revision file")
                open(dest, 'w').write(output)
        elif os.path.exists(bzr_src):
            info("Copying bzr revision file")
            copyfile(bzr_src, dest)
        return retval


def get_site_packages_dir(*dirs):
    """
    Gets the relative path of the site-packages directory

    This is mainly useful for setup.py set usage:

        >>> data_files = [get_site_packages_dir('foo')]

    where files is a list of files to be installed in
    a directory called foo created in your site-packages directory

    :param dirs: directory names to be appended
    """
    python_version = sys.version_info[:2]
    libdir = get_python_lib(plat_specific=False,
                            standard_lib=True, prefix='')
    if python_version < (2, 6):
        site = 'site-packages'
    else:
        site = 'dist-packages'
    return os.path.join(libdir, site, *dirs)


def listfiles(*dirs):
    """
    Lists all files in directories and optionally uses basic shell
    matching, example:

    >>> listfiles('data', 'glade', '*.glade')
    ['data/glade/Foo.glade', 'data/glade/Bar.glade', ...]

    :param dirs: directory parts
    """

    dir, pattern = os.path.split(os.path.join(*dirs))
    abspath = os.path.abspath(dir)
    if not os.path.exists(abspath):
        # TODO: Print a warning here?
        return []
    return [os.path.join(dir, filename)
            for filename in os.listdir(abspath)
            if filename[0] != '.' and fnmatch(filename, pattern)]


def compile_po_files(domain, dirname='locale'):
    """
    Compiles po files to mo files.
    Note. this function depends on gettext utilities being installed

    :param domain: gettext domain
    :param dirname: base directory
    :returns: a list of po files
    """
    data_files = []
    for po in listfiles('po', '*.po'):
        lang = os.path.basename(po[:-3])
        mo = os.path.join(dirname, lang, 'LC_MESSAGES', domain + '.mo')

        if not os.path.exists(mo) or newer(po, mo):
            directory = os.path.dirname(mo)
            if not os.path.exists(directory):
                info("creating %s" % directory)
                os.makedirs(directory)
            try:
                p = subprocess.Popen(['msgfmt', '-o', mo, po],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            except OSError:
                warn('msgfmt is missing, not installing translations')
                return []
            info('compiled %s -> %s' % (po, mo))
            p.communicate()

        dest = os.path.dirname(os.path.join('share', mo))
        data_files.append((dest, [mo]))

    return data_files


def listpackages(root, exclude=None):
    """Recursivly list all packages in directory root
    Optionally exclude can be specified which is a string
    like foo/bar.

    :param root: directory
    :param exclude: optional packages to be skipped
    """

    packages = []
    if not os.path.exists(root):
        raise ValueError("%s does not exists" % (root,))

    if not os.path.isdir(root):
        raise ValueError("%s must be a directory" % (root,))

    if os.path.exists(os.path.join(root, '__init__.py')):
        packages.append(root.replace('/', '.'))

    for filename in os.listdir(root):
        full = os.path.join(root, filename)
        if os.path.isdir(full):
            packages.extend(listpackages(full))

    if exclude:
        for package in packages[:]:
            if package.startswith(exclude):
                packages.remove(package)

    return packages


def setup(**kwargs):
    """
    A drop in replacement for distutils.core.setup which
    integrates nicely with kiwi.environ
    :attribute resources:
    :attribute global_resources:
    :attribute templates: List of templates to install
    """
    resources = {}
    global_resources = {}
    templates = []
    if 'resources' in kwargs:
        resources = kwargs.pop('resources')
    if 'global_resources' in kwargs:
        global_resources = kwargs.pop('global_resources')
    if 'templates' in kwargs:
        templates = kwargs.pop('templates')

    def run_install(self):
        name = kwargs.get('name')
        if name:
            self.data_files.extend(compile_po_files(name))
        KiwiInstallData.run(self)

        varext = _VariableExtender(self.distribution)

        for path, files in templates:
            # Skip templates inside eggs for now
            if 'bdist_egg' in self.distribution.commands:
                continue
            install = self.distribution.get_command_obj('install')
            target = os.path.join(install.prefix, path)
            if install.root:
                if target[0] == '/':
                    target = target[1:]
                target = os.path.join(install.root, target)

            if not os.path.exists(target):
                info("creating %s" % target)
                os.makedirs(target)

            for filename in files:
                data = open(filename).read()
                data = varext.extend(data)
                target_file = os.path.join(target, os.path.basename(filename))
                info('installing template %s' % target_file)
                open(target_file, 'w').write(data)

    # distutils uses old style classes
    InstallData = new.classobj('InstallData', (KiwiInstallData,),
                               dict(run=run_install))
    InstallLib = new.classobj('InstallLib', (KiwiInstallLib,),
                              dict(resources=resources,
                                   global_resources=global_resources))
    cmdclass = dict(install_data=InstallData, install_lib=InstallLib,
                    clean=KiwiClean)
    kwargs.setdefault('cmdclass', cmdclass).update(cmdclass)

    DS_setup(**kwargs)
