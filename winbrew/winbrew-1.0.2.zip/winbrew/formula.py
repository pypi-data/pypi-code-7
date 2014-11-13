import subprocess
import sys
import os
import zipfile
import tarfile
import urllib2
import errno
import glob
import shutil
import shlex
import imp
import winbrew
import argparse
import hashlib
from winbrew.manifest import Manifest

# Default arguments for the supported build tools
cmake_args = ('-G', 'Visual Studio 12')
msbuild_args = ('/P:Configuration=Release','/p:PlatformToolset=v120')

class FormulaException(Exception):
    pass

class Formula:
    """
    A formula describes all the steps that must be taken to build the package.
    The package is downloaded from the URL given in the subclass body to the
    WinBrew cache dir, and then extracted, built, and installed to the WinBrew
    header/library directories.
    """
    def __init__(self):
        self.filename = os.path.split(self.url)[1]
        self.ext = os.path.splitext(self.filename)[1]
        self.name = self.__class__.__name__.lower()
        self.workdir = os.path.abspath(os.path.join(winbrew.cache_path, self.name))
        self.manifest = Manifest(self.name)
        try:
            self.options
        except AttributeError:
            self.options = {}

    def parse_options(self, args):
        """
        Parse formula options.
        """
        parser = argparse.ArgumentParser(prog=self.name)
        for name, desc in self.options.iteritems(): 
            parser.add_argument('--%s' % name, action='store_true', help=desc)
        parser.add_argument('remainder', nargs=argparse.REMAINDER)
        self.selected_options = parser.parse_args(args)
        return self.selected_options.remainder

    def option(self, name):
        """
        Returns the value of the selected option, as set by the user.  If the
        option is not set, then return the default value.
        """
        return getattr(self.selected_options, name.replace('-', '_'))

    def install(self):
        """
        Installs the package.
        """
        pass

    def test(self):
        """
        Tests the package.
        """
        pass

    def download(self):
        """
        Download from the source URL via HTTP or git
        """
        print('downloading %s' % self.name)
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)
        os.chdir(self.workdir)
        if self.ext == '.git':
            if not os.path.exists(self.name):
                subprocess.check_call(shlex.split('git clone %s %s' % (self.url, self.name)))
            self.unpack_name = self.name
        else:
            if not os.path.exists(self.filename): 
                stream = urllib2.urlopen(self.url)
                fd = open(self.filename, 'wb')
                shutil.copyfileobj(stream, fd)
                fd.close()

    def sha1_update_for_file(self, sha1, filename):
        """
        Verify one file
        """
        fd = open(filename, 'rb')
        chunk_size = 8192
        while True:
            data = fd.read(chunk_size)
            if not data:
                break
            sha1.update(data)

    def verify(self):
        """
        Check the downloaded package against the hash
        """
        sha1 = hashlib.sha1()

        if os.path.isfile(self.filename):
            self.sha1_update_for_file(sha1, self.filename)
        elif os.path.isdir(self.workdir):
            for subdir, dirs, files in os.walk(self.workdir):
                files = [f for f in files if not f[0] == '.']
                dirs[:] = [d for d in dirs if not d[0] == '.']
                for file in files:
                    self.sha1_update_for_file(sha1, os.path.join(subdir, file))
        else:
            raise FormulaException("can't verify package %s: downloaded file not found" % self.name)

        if self.sha1 != sha1.hexdigest():
            raise FormulaException("can't verify package %s: hash doesn't match: %s" % (self.name, sha1.hexdigest()))

    def unpack(self):
        """
        Extract the project from its zip/tar file if necessary
        """
        print('unpacking %s' % self.name)
        os.chdir(self.workdir)
        if self.ext == '.zip':
            self.unzip()
        elif self.ext == '.gz':
            self.untar()
        elif self.ext == '.tgz':
            self.untar()
        elif self.ext == '.bz2':
            self.untar(compression='bz2')
        elif self.ext == '.msi':
            self.msi()
        elif self.ext == '.git':
            pass
        else:
            raise Exception('unknown file type')

    def setup(self):
        """
        Prepare the package for installation -- then install it.
        """
        print('installing %s' % self.name)
        os.chdir(self.workdir)
        try:
            os.chdir(self.unpack_name)
        except OSError, e:
            pass # Unpack name was not a directory
        self.install()

    def cd(self, path):
        """
        Change directories.  Generally used by formulas in the install() method
        """
        os.chdir(path)

    def msi(self):
        """
        Install a MSI-style installer
        """
        self.system('msiexec /i %s' % self.filename)
        self.unpack_name = '.'

    def unzip(self):
        """
        Unzip the downloaded zip file into the current working directory
        """ 
        fd = open(self.filename, 'rb')
        zf = zipfile.ZipFile(fd)
        self.unpack_name = os.path.commonprefix(zf.namelist())
        if os.path.exists(self.unpack_name):
            pass # already extracted
        else:
            zf.extractall()

    def untar(self, compression='gz'):
        """
        Extract the downloaded tar file into the current working directory
        """
        tf = tarfile.open(self.filename, mode='r:%s' % compression)
        self.unpack_name = os.path.commonprefix(tf.getnames())
        if os.path.exists(self.unpack_name):
            pass 
        else:
            tf.extractall()

    def system(self, cmd, shell=False):
        """
        Run a build command.  Used by formulas in the install() method
        """
        subprocess.check_call(shlex.split(cmd), shell=shell)

    def nmake(self, args=()):
        """
        Run nmake.  Optionally, the caller can set the arguments to pass to nmake.
        """
        subprocess.check_call(('nmake',)+args)

    def cmake(self, args=cmake_args):
        """
        Run cmake.  Optionally, the caller can set arguments to pass to cmake.
        """
        subprocess.check_call(('cmake',)+args)

    def scons(self, args=()):
        """
        Run scons.  Optionally, the caller can set arguments to pass to scons.
        """
        subprocess.check_call(('scons',)+args, shell=True)

    def msbuild(self, args=msbuild_args):
        """
        Run msbuild.  Optionally, the caller can set arguments to pass to msbuild.
        """
        subprocess.check_call(('msbuild',)+args)

    def libs(self, path):
        """
        Specify a folder containing library files (DLLs and static libraries). 
        All library files in the folder are copied to the winbrew library folder.
        """
        if path[-1] != '\\':
            path += '\\'
        for root, dirs, files in os.walk(path):
            td = os.path.join(winbrew.lib_path, root.replace(path, ''))
            if not os.path.exists(td):
                os.makedirs(td)
            for fn in files:
                lib_files = ('.pdb', '.dll', '.lib', '.exp')
                if os.path.splitext(fn)[1] in lib_files:
                    tf = os.path.join(td, fn)
                    shutil.copyfile(os.path.join(root, fn), tf)
                    self.manifest.files.append(tf)

    def lib(self, path, dest=''):
        """
        Specify a library file to be installed.
        """
        td = os.path.join(winbrew.lib_path, os.path.dirname(dest))
        if not os.path.exists(td):
            os.makedirs(td)
        if dest:
            tf = os.path.join(td, os.path.basename(dest))
        else:
            tf = os.path.join(td, os.path.split(path)[-1])
        shutil.copyfile(path, tf)
        self.manifest.files.append(tf)

    def includes(self, path, dest=''):
        """
        Specify a folder containing C or C++ header files.  All header files in
        the folder are copied to the winbrew library folder.
        """
        if path[-1] != '\\':
            path += '\\'
        for root, dirs, files in os.walk(path):
            td = os.path.join(winbrew.include_path, dest, root.replace(path, ''))
            for fn in files:
                header_files = ('.h', '.hpp', '.hh', '.inl')
                if os.path.splitext(fn)[1] in header_files:
                    if not os.path.exists(td):
                        os.makedirs(td)
                    tf = os.path.join(td, fn)
                    shutil.copyfile(os.path.join(root, fn), tf)
                    self.manifest.files.append(tf)

    def include(self, path, dest=''):
        """
        Specify a single header file.  The file is copied to the winbrew include
        folder.
        """
        td = os.path.join(winbrew.include_path, os.path.dirname(dest))
        if not os.path.exists(td):
            os.makedirs(td)
        if dest:
            tf = os.path.join(td, os.path.basename(dest))
        else:
            tf = os.path.join(td, os.path.split(path)[-1])
        shutil.copyfile(path, tf)
        self.manifest.files.append(tf)

    def bin(self, path, dest=''):
        """
        Specify a single binary executable.  The file is copied to the winbrew 
        binaries bolder.
        """
        td = os.path.join(winbrew.bin_path, os.path.dirname(dest))
        if not os.path.exists(td):
            os.makedirs(td)
        if dest:
            tf = os.path.join(td, os.path.basename(dest))
        else:
            tf = os.path.join(td, os.path.split(path)[-1])
        shutil.copyfile(path, tf)
        self.manifest.files.append(tf)

    def mkdir(self, path):
        try:
            os.makedirs(os.path.join(winbrew.home, path))
        except OSError, e:
            pass

    def copy(self, path, dest=''):
        """
        Copies files found at 'path' to a subfolder of winbrew.home
        """
        for root, dirs, files in os.walk(path):
            td = os.path.join(winbrew.home, dest, root)
            for fn in files:
                if not os.path.exists(td):
                    os.makedirs(td)
                tf = os.path.join(td, fn)
                shutil.copyfile(os.path.join(root, fn), tf)
                self.manifest.files.append(tf)
    
    def error(self, msg):
        """
        Indicates that there was an error while building the package.
        """
        sys.stderr.write('error: %s: %s' % (self.name, msg))
        sys.stderr.flush()
        sys.exit(1)

    @staticmethod
    def formula_by_name(name):
        """
        Finds the formula class for the given formula name.  Throws an exception 
        if the formula doesn't exist.  Looks for a module in the formula dir first;
        if the module isn't found there, falls back to the default installation.
        """
        try:
            full_name = 'winbrew.formula.%s' % name
            path = os.path.join(winbrew.formula_path, '%s.py' % name)
            module = imp.load_source(full_name, path)
        except IOError, e:
            raise FormulaException('formula "%s" not found' % name)
        return getattr(module, name.title())


