#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""
from genericpath import isfile, isdir
import hashlib
import logging
from os.path import join
import sys

import sh

logger = logging.getLogger(__name__)

def _print(text):
    print(text)
    sys.stdout.flush()

def rm(path):
    return sh.rm("-rf", path, _ok_code=[0, 1])

def md5(i):
    h = hashlib.new("md5")
    h.update(i.encode("utf-8"))
    return h.hexdigest()

class Python(object):

    def __init__(self, version, installdir, cachedir=None, url=None):
        self.version = version

        if not url:
            url = "https://www.python.org/ftp/python/%s/Python-%s.tgz" % (version, version)
        self.python_url = url
        self.python_fname = self.python_url.split("/")[-1]

        self.installdir = installdir
        self.pip_binary = "%s/bin/pip3" % self.installdir

        if not cachedir:
            cachedir = "/var/lib/buildutils/python/%s/%s" % (self.version, md5(self.installdir))

        self.cachedir = cachedir
        sh.mkdir("-p", self.cachedir)

        self.python_tgz_path = self.cachedir + "/" + self.python_fname
        self.extract_dir = self.cachedir + "/" + ".".join(self.python_fname.split(".")[:-2])
        self.extract_py_dir = "%s/Python-%s" % (self.extract_dir, version)
        self.python_binary = "%s/python" % self.extract_py_dir

        self.cache_build_dir = self.cachedir + "/build"
        self.cache_build_verify_file = self.cache_build_dir + ".ok"

        # make directories and ensure permissions
        sh.mkdir("-p", self.cachedir)
        sh.mkdir("-p", self.cache_build_dir)
        sh.chmod("-R", "777", self.cachedir, _ok_code=[0, 1])

    def download(self):
        _print("download python: %s" % self.python_url)

        cache_path = self.python_tgz_path + ".cache"

        if isfile(cache_path) and isfile(self.python_tgz_path):
            _print("download python: Using cached file")
            return

        sh.wget(self.python_url, "-nc", "-O", self.python_tgz_path, _ok_code=[0, 1])
        if not isfile(self.python_tgz_path):
            _print("ERROR: unable to download %s" % self.python_url)
            sys.exit(1)

        sh.touch(cache_path)

    def extract(self):
        _print("extracting python: %s" % self.python_tgz_path)
        cache_path = self.extract_dir + ".cache"

        if isfile(cache_path):
            _print("extracting python: Using cached extract dir")
            return

        sh.mkdir("-p", self.extract_dir)
        sh.tar.xf(self.python_tgz_path, directory=self.extract_dir)
        sh.touch(cache_path)

    def build(self):
        self.clean()
        self.download()
        self.extract()

        cache_path = self.extract_py_dir + ".cache"

        if isfile(cache_path):
            _print("building python: using prebuilt from cache")
        else:
            _print("building python: configure")
            sh.sh("%s/configure" % self.extract_py_dir, prefix=self.installdir, _cwd=self.extract_py_dir)
            _print("building python: make")
            sh.make(_cwd=self.extract_py_dir)
            sh.touch(cache_path)

        _print("building python: make install")
        sh.make.install(_cwd=self.extract_py_dir)

        self.python_binary = join(self.installdir, "bin/python3.4")

    def install_pip(self):
        _print("installing pip")
        sh.wget("https://bootstrap.pypa.io/get-pip.py", _cwd=self.extract_dir)
        self._exec("%s/get-pip.py" % self.extract_dir, _cwd=self.installdir, _out=sys.stdout)

    def install_requirements(self, requirements_path):
        """
        Installs a requirements txt file. Acts like:
            pip install -r <requirements_path>

        :param requirements_path:
        :return:
        """
        sh.Command(self.python_binary)("-OO", self.pip_binary, "install", "-r", requirements_path, _cwd=self.installdir)

    def compileall(self, directory):
        """

        :param directory:
        :return:
        """
        assert isdir(directory)

        sh.find("-name", "*.whl", "-delete", _cwd=directory)
        sh.find("-name", "*.exe", "-delete", _cwd=directory)
        sh.find("-name", "*.pyc", "-delete", _cwd=directory)
        sh.find("-name", "*.pyo", "-delete", _cwd=directory)
        sh.find("-name", "__pycache__", "-delete", _cwd=directory)

        sh.Command(join(self.installdir, "bin", "python3"))("-OO", "-m", "compileall", "-f", "-b", directory)

        sh.find("-name", "*.py", "-delete", _cwd=directory)
        sh.find("-name", "*.pyc", "-delete", _cwd=directory)

    def clean(self):
        _print("cleaning previous stuff")
        # rm(self.installdir)
        # rm(self.extract_dir)

    def cleanup_compiled_files(self, directory):
        """
        Removes compiled files like *.pyc and *.pyo
        :param directory:
        :return:
        """
        _print("cleanup compiled files in: %s" % directory)
        sh.find("-name", "*.pyc", "-delete", _cwd=directory)
        sh.find("-name", "*.pyo", "-delete", _cwd=directory)
        sh.find("-name", "__pycache__", "-delete", _cwd=directory)

    def cleanup(self):
        """
        Cleaning up python installation. This removes things that are not really essential for a portable python, such
        like:
          * header files
          * commonly not used libraries like tkinter or sqlite3
          * documentation

        @return:
        """
        _print("cleaning up python installation")

        def rm(path):
            sh.rm("-rf", join(self.installdir, path))

        rm("include")
        rm("lib/libpython3.4m")
        rm("lib/libpython3.4m.a")
        rm("lib/python3.4/lib2to3")
        rm("lib/python3.4/sqlite3")
        rm("lib/python3.4/test")
        rm("lib/python3.4/tkinter")
        rm("lib/pkgconfig")
        rm("share")

        self.cleanup_compiled_files(join(self.installdir, "lib"))

    def _exec(self, *cmd, **kwargs):
        sh.Command(self.python_binary)(*cmd, **kwargs)