#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2014, Yung-Yu Chen <yyc@solvcon.net>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the pstake nor the names of its contributors may be
#   used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


"""Convert a pstricks LaTeX file (.tex) to an image file."""


import sys
import os
import glob
import contextlib
import argparse
import tempfile
import shutil


__version__ = "0.1.1"


@contextlib.contextmanager
def _remember_cwd():
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)


class Command(object):
    def __init__(self, command, prefix_path=None):
        self.command = command
        self.prefix_path = prefix_path

    def __call__(self, *args):
        param = " ".join(args)
        with _remember_cwd():
            if self.prefix_path:
                os.chdir(self.prefix_path)
            cmd = " ".join([self.command, param])
            sys.stdout.write(cmd + '\n')
            sys.stdout.flush()
            os.system(cmd)


_TEX_TEMPLATE = r'''\documentclass[%sletterpaper,dvips]{article}
\usepackage[usenames]{color}
\usepackage{pst-all}
\usepackage{pst-3dplot}
\usepackage{pst-eps}
\usepackage{pst-coil}
\usepackage{pst-bar}
\usepackage{multido}
\usepackage{cmbright}
\usepackage{fancyvrb}
\begin{document}
\pagestyle{empty}
\begin{TeXtoEPS}
%s
\end{TeXtoEPS}
\end{document}'''


class Pstricks(object):
    def __init__(self, verbosity=3, keep_tmp=False, **kw):
        self.verbosity = verbosity
        self.keep_tmp = keep_tmp
        self.tmp_main = 'makeeps_tmp'
        self.tex_template = _TEX_TEMPLATE
        self.cmd_latex = Command("latex")
        self.cmd_dvips = Command("dvips")
        self.cmd_convert = Command("convert")

    def pst(self, src, dst, options=None):
        # Sanitize options.
        options = ','.join([] if None is options else options)
        if options:
            options += ','
        # Prepare TeX data.
        tex = self.tex_template % (options, open(src).read())
        tmpf = open(self.tmp_main+'.tex', 'w').write(tex)
        self.cmd_latex(self.tmp_main+'.tex')
        self.cmd_dvips(self.tmp_main+'.dvi', '-E -o %s' % dst)
        if not self.keep_tmp:
            for fn in glob.glob(self.tmp_main+'.*'):
                os.unlink(fn)

    def imconvert(self, src, dst, dpi=300):
        self.cmd_convert('-density %d -units PixelsPerInch %s %s' % (
            dpi, src, dst))

    def __call__(self, fn):
        with _remember_cwd():
            os.chdir(fn.tempdir)
            sys.stdout.write("Working in %s ...\n" % os.getcwd())
            if 'eps' == fn.ftype:
                self.pst(fn.sourcepath, fn.intereps)
                shutil.copyfile(fn.intereps, fn.destpath)
            elif 'png' == fn.ftype:
                self.pst(fn.sourcepath, fn.intereps)
                self.imconvert(fn.intereps, fn.destpath)
                if self.keep_tmp:
                    shutil.copyfile(fn.intereps,
                                    os.path.join(fn.destdirabs, fn.intereps))
            else:
                sys.stdout.write("Destination file type %s isn't supported.\n" %
                                 dstext)
        sys.stdout.write("Removing the temporary working directory %s ... " % fn.tempdir)
        shutil.rmtree(fn.tempdir)
        sys.stdout.write("Done\n")


class Filename(object):
    def __init__(self, source, dest, ftype=''):
        """
        >>> Filename(source='dir1/main.tex', dest='dir2/', ftype='png')
        Filename(source='dir1/main.tex', dest='dir2/main.png')
        >>> Filename(source='dir1/main.tex', dest='dir2/other.png')
        Filename(source='dir1/main.tex', dest='dir2/other.png')
        >>> Filename(source='dir1/main.tex', dest='dir2/other.png', ftype='png')
        Traceback (most recent call last):
            ...
        ValueError: can't set both dest and ftype
        >>> Filename(source='dir1/main.tex', dest='dir2/')
        Traceback (most recent call last):
            ...
        ValueError: either dest or ftype needs to be specified
        """
        # Sanitize source file name.
        if not source.lower().endswith(".tex"):
            source += ".tex"
        # Compute source directory.
        sourcedir, sourcebase = os.path.split(source)
        sourcedirabs = os.path.abspath(sourcedir)
        # Compute source file main name.
        sourcemain = os.path.splitext(sourcebase)[0]
        # Compute destination directory.
        if dest:
            destdir, destbase = os.path.split(dest)
        else:
            destdir = destbase = ''
        destdirabs = os.path.abspath(destdir)
        # Compute destination file name.
        if destbase:
            if ftype:
                raise ValueError('can\'t set both dest and ftype')
            destmain, destext = os.path.splitext(destbase)
            destext = destext.strip('.')
        elif ftype:
            destmain, destext = sourcemain, ftype
        else:
            raise ValueError('either dest or ftype needs to be specified')
        # Sanitize destination file extension name.
        destext = destext.lower()
        # Set to self.
        self.sourcedir = sourcedir
        self.sourcedirabs = sourcedirabs
        self.sourcebase = sourcebase
        self.sourcemain = sourcemain
        self.destdir = destdir
        self.destdirabs = destdirabs
        self.destmain = destmain
        self.destext = destext
        # Temporary directory.
        self._tempdir = None

    def __repr__(self):
        return "%s(source='%s', dest='%s')" % (
            self.__class__.__name__,
            os.path.join(self.sourcedir, self.source),
            os.path.join(self.destdir, self.dest))

    @property
    def tempdir(self):
        """
        Return a temporary directory.  If it doesn't exist yet, create one.
        """
        if None is self._tempdir:
            self._tempdir = tempfile.mkdtemp()
        return self._tempdir

    @property
    def source(self):
        """
        >>> Filename(source='dir1/name.tex', dest='dir2/', ftype='png').source
        'name.tex'
        """
        return self.sourcebase

    @property
    def dest(self):
        """
        >>> Filename(source='dir1/name.tex', dest='dir2/', ftype='png').dest
        'name.png'
        >>> Filename(source='dir1/name.tex', dest='dir2/', ftype='eps').dest
        'name.eps'
        """
        return '.'.join([self.destmain, self.destext])

    @property
    def sourcepath(self):
        """
        >>> fn = Filename(source='dir1/name.tex', dest='dir2/', ftype='png')
        >>> fn.sourcepath.endswith(fn.source)
        True
        """
        return os.path.join(self.sourcedirabs, self.source)

    @property
    def destpath(self):
        """
        >>> fn = Filename(source='dir1/name.tex', dest='dir2/', ftype='png')
        >>> fn.destpath.endswith(fn.dest)
        True
        """
        return os.path.join(self.destdirabs, self.dest)

    @property
    def ftype(self):
        """
        >>> Filename(source='dir1/name.tex', dest='dir2/', ftype='png').ftype
        'png'
        >>> Filename(source='dir1/name.tex', dest='dir2/other.png').ftype
        'png'
        """
        return self.destext

    @property
    def intereps(self):
        """
        >>> Filename(source='dir1/name.tex', dest='dir2/', ftype='png').intereps
        'name.eps'
        """
        return '.'.join([self.destmain, 'eps'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-V', '--version', action='version',
                        version='%%(prog)s %s' % __version__)
    parser.add_argument('src', type=str,
                        help='source file name')
    parser.add_argument('dst', type=str, nargs='?', default=None,
                        help='destination file name')
    parser.add_argument('-k', dest='keep_tmp', action='store_true',
                        default=False,
                        help='keep temporary files')
    parser.add_argument('-t', dest='dstext', type=str, action='store',
                        default='png',
                        help='destination file type '
                             '(default = %(default)s)')
    parser.add_argument('-v', '--verbose', dest='verbosity', action='store',
                        type=int, default=3,
                        help='verbosity of output (1-5) '
                             '(default = %(default)d)') # FIXME: not used.
    args = parser.parse_args()

    runner = Pstricks(**vars(args))
    fn = Filename(source=args.src, dest=args.dst, ftype=args.dstext)
    runner(fn)

    return 0


if __name__ == '__main__':
    main()
