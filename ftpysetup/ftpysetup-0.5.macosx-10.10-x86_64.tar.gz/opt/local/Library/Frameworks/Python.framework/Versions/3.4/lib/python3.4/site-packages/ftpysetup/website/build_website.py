#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""Implements a setuptools ``build_website`` command."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.5'
__copyright__ = """Copyright (C) 2014 Lance Helsten"""
__docformat__ = "reStructuredText en"
__license__ = """
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

__all__ = ['WebDistribution', 'BuildWebsite']

import sys
if sys.version_info < (3, 3):
    raise Exception("venv requires Python 3.3 or higher.")
import os
import errno
import shutil
import configparser
import subprocess
import setuptools

class WebDistribution(setuptools.Distribution):
    def __init__(self, attrs=None):
        self.websites = None
        super().__init__(attrs)

class BuildWebsite(setuptools.Command):
    """Generate the website from reStructured text files."""

    user_options = [
        ('force=', 'f', "Forcibly build everything (ignore file timestamps)"),
        ('debug', 'g', "Compile extensions and libraries with debugging information"),
        ('template=', None, "Path to template map file."),
        ('rst2html=', None, "Path to rst2html.py executable.")
        ]
    boolean_options = ['force', 'debug']

    def initialize_options(self):
        self.build_base = 'build'
        self.force = False
        self.debug = None
        self.template = None
        self.rst2html = None

    def finalize_options(self):
        self.set_undefined_options('build',
                ('force', 'force'),
                ('debug', 'debug'))

        if self.template == None:
            sys.exit("Path to template map file required.")
        self.template = os.path.expandvars(self.template)
        self.template = os.path.expanduser(self.template)
        self.template = os.path.abspath(self.template)
        with open(self.template) as f:
            self.template = eval(f.read())

        if self.rst2html is None:
            r2hout = subprocess.check_output(['python-config', '--prefix'])
            r2hout = str(r2hout, encoding='utf-8').strip()
            self.rst2html = os.path.join(r2hout, 'bin', 'rst2html.py')
        else:
            self.rst2html = os.path.expandvars(self.rst2html)
            self.rst2html = os.path.expanduser(self.rst2html)
            self.rst2html = os.path.abspath(self.rst2html)

    def run(self):
        for website in self.distribution.websites:
            self.copy_filetypes(website, '.html', 'HTML')
            self.copy_filetypes(website, '.xml', 'XML')
            self.copy_filetypes(website, '.xsd', 'XSD')
            self.copy_filetypes(website, '.css', 'CSS2')
            self.copy_filetypes(website, '.py', 'Python')
            self.copy_filetypes(website, '.js', 'JavaScript')
            self.copy_filetypes(website, '.jpg', 'JPEG')
            self.copy_filetypes(website, '.png', 'PNG')
            self.copy_filetypes(website, '.gif', 'GIF')
            self.copy_filetypes(website, '.ico', 'Favicon')
            self.copy_filetypes(website, '.yaml', 'YAML')
            self.generate_html(website)

    def generate_html(self, website):
        args = [self.rst2html,
                "--traceback",
                "TEMPLATE_ARG",
                "SRC_PATH_ARG_2",
                "DST_PATH_ARG_3"]

        configs = []
        for pathfrag, cfgpath in self.template.items():
            cfgmtime = os.path.getmtime(cfgpath)
            cfg = configparser.ConfigParser()
            cfg.read(cfgpath)
            tmppath = cfg["html4css1 writer"]["template"]
            tmpmtime = os.path.getmtime(tmppath)
            configs.append((pathfrag, cfgpath, max(cfgmtime, tmpmtime)))
        configs.sort(reverse=True)

        #Process reStructuredText files
        try:
            for dirpath, dirnames, filenames in os.walk(website):
                filenames = [os.path.join(dirpath, f) for f in filenames if os.path.splitext(f)[1] == '.rst']
                for f in filenames:
                    src = os.path.abspath(f)
                    srcmtime = os.path.getmtime(src)

                    dst = os.path.abspath(
                        os.path.join(self.build_base, os.path.splitext(f)[0] + ".html"))
                    dstmtime = os.path.getmtime(dst) if os.path.exists(dst) else 0

                    for pathfrag, cfg, cfgmtime in configs:
                        if dirpath.startswith(pathfrag):
                            break
                    else:
                        raise OSError("Unable to match configuration to path.")

                    args[-3] = "=".join(["--config", cfg])

                    if self.force or not os.path.isfile(dst) or srcmtime > dstmtime or cfgmtime > dstmtime:
                        if not os.path.exists(os.path.dirname(dst)):
                            os.makedirs(os.path.dirname(dst))
                        print("Generating HTML5/CSS2 for", f)
                        args[-2] = src
                        args[-1] = dst
                        ret = subprocess.call(args)
        except OSError as err:
            if err.errno == errno.ENOENT:
                print("error: Docutils missing.", file=sys.stderr)
            raise err

    def copy_filetypes(self, website, ext, mediatype):
        srcdir = os.path.join(self.build_base, website)
        for dirpath, dirnames, filenames in os.walk(website):
            files = [f for f in filenames if os.path.splitext(f)[1] == ext]
            for f in files:
                src = os.path.join(dirpath, f)
                dst = os.path.join(self.build_base, dirpath, f)
                if not os.path.isdir(os.path.dirname(dst)):
                    os.makedirs(os.path.dirname(dst))
                if (self.force
                or not os.path.isfile(dst)
                or os.path.getmtime(src) > os.path.getmtime(dst)):
                    print("Copy", mediatype, src)
                    shutil.copy(src, dst)

    def has_restructured_text(self):
        return True



