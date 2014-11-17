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


__version__ = "0.2"


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


_TEX_TEMPLATE = r'''\documentclass[%(options)sletterpaper,dvips]{article}
\usepackage[usenames]{color}
\usepackage{pst-all}
\usepackage{pst-3dplot}
\usepackage{pst-eps}
\usepackage{pst-coil}
\usepackage{pst-bar}
\usepackage{multido}
\usepackage{fancyvrb}
%(packages)s
\begin{document}
\pagestyle{empty}
\begin{TeXtoEPS}
%(code)s
\end{TeXtoEPS}
\end{document}'''


class Pstricks(object):
    def __init__(self, verbosity=3, **kw):
        self.verbosity = verbosity
        self.tex_template = _TEX_TEMPLATE
        self.cmd_latex = Command("latex")
        self.cmd_dvips = Command("dvips")
        self.cmd_convert = Command("convert")

    def write_tex(self, src, dst, cmbright=False, options=None, packages=None):
        # Sanitize options.
        options = ','.join([] if None is options else options)
        if options:
            options += ','
        # Sanitize packages.
        packages = [] if None is packages else packages
        if cmbright:
            cmbright = "\usepackage{cmbright}"
            if not packages or cmbright not in packages:
                packages.insert(0, cmbright)
        packages = '\n'.join(packages)
        # Prepare TeX data.
        data = dict(options=options, packages=packages, code=open(src).read())
        tex = self.tex_template % data
        # Write the TeX data to the destination file.
        with open(dst, 'w') as tmpf:
            tmpf.write(tex)

    def pst(self, srcmain, dst):
        self.cmd_latex(srcmain+'.tex')
        self.cmd_dvips(srcmain+'.dvi', '-E -o %s' % dst)

    def imconvert(self, src, dst, dpi=300):
        self.cmd_convert('-density %d -units PixelsPerInch %s %s' % (
            dpi, src, dst))

    def __call__(self, fn, cmbright=None, keep_tmp=None, **kw):
        with _remember_cwd():
            os.chdir(fn.tempdir)
            sys.stdout.write("Working in %s ...\n" % os.getcwd())
            cmbright = "cmbright" == cmbright
            self.write_tex(fn.sourcepath, fn.intertex, cmbright=cmbright)
            self.pst(fn.destmain, fn.intereps)
            if 'eps' == fn.ftype:
                shutil.copyfile(fn.intereps, fn.destpath)
            elif 'png' == fn.ftype:
                self.imconvert(fn.intereps, fn.destpath)
            else:
                sys.stdout.write("Destination file type %s isn't supported.\n" %
                                 dstext)
        tempdir = os.path.abspath(fn.tempdir)
        if not keep_tmp:
            sys.stdout.write(
                "Removing the temporary working directory %s ... " % tempdir)
            shutil.rmtree(fn.tempdir)
            sys.stdout.write("Done\n")
        else:
            sys.stdout.write(
                "Temporary files were kept in the directory %s\n" % tempdir)


class Filename(object):
    def __init__(self, source, dest='', ftype='', tempdir=None):
        """
        This class is responsible for determining the file names to be used in
        :py:class:`Pstricks`.

        One should specify either the *dest* argument with an extension name or
        the *ftype* argument.

        >>> # Good.
        >>> Filename(source='dir1/main.tex', dest='dir2/', ftype='png')
        Filename(source='dir1/main.tex', dest='dir2/main.png')
        >>> # Good.
        >>> Filename(source='dir1/main.tex', dest='other.png')
        Filename(source='dir1/main.tex', dest='other.png')
        >>> # Good.
        >>> Filename(source='dir1/main.tex', dest='', ftype='png')
        Filename(source='dir1/main.tex', dest='main.png')

        Construction should fail if the extension name of the destination file
        can't be determined:

        >>> Filename(source='dir1/main.tex', dest='other')
        Traceback (most recent call last):
            ...
        ValueError: can't determine the destination file type
        >>> Filename(source='dir1/main.tex')
        Traceback (most recent call last):
            ...
        ValueError: either dest or ftype needs to be specified

        If both *dest* and *ftype* are given, the extension name of the
        destination file is deduced from *dest* if possible.  If *dest* doesn't
        contain the extension name, use *ftype*.

        >>> Filename(source='dir1/main.tex', dest='dir2/other.png', ftype='eps')
        Filename(source='dir1/main.tex', dest='dir2/other.png')
        >>> Filename(source='dir1/main.tex', dest='dir2/other', ftype='eps')
        Filename(source='dir1/main.tex', dest='dir2/other.eps')
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
        if not destdir and os.path.isdir(destbase):
            destdir, destbase = destbase, ''
        destdirabs = os.path.abspath(destdir)
        # Compute destination file name.
        if destbase:
            destmain, destext = os.path.splitext(destbase)
            destext = destext.strip('.')
            destext = destext if destext else ftype
        elif ftype:
            destmain, destext = sourcemain, ftype
        else:
            raise ValueError("either dest or ftype needs to be specified")
        if not destext:
            raise ValueError("can't determine the destination file type")
        # Sanitize destination file extension name.
        destext = destext.lower()
        # Set to self.
        #: Relative directory of the source file.
        self.sourcedir = sourcedir
        #: Absolute directory of the source file.
        self.sourcedirabs = sourcedirabs
        #: Base name of the source file.
        self.sourcebase = sourcebase
        #: Main part of the base name of the source file.
        self.sourcemain = sourcemain
        #: Relative directory of the destination file.
        self.destdir = destdir
        #: Absolute directory of the destination file.
        self.destdirabs = destdirabs
        #: Main part of the base name of the destination file.
        self.destmain = destmain
        #: Extension part of the base name of the destination file.  It is
        #: always lower-case.
        self.destext = destext
        # See :py:attr:`tempdir`.
        self._tempdir = tempdir

    def __repr__(self):
        return "%s(source='%s', dest='%s')" % (
            self.__class__.__name__,
            os.path.join(self.sourcedir, self.source),
            os.path.join(self.destdir, self.dest))

    @property
    def tempdir(self):
        """
        Return a temporary directory.  If it doesn't exist, create a new one.

        The constructor can specify an existing directory as the temporary
        directory.

        Note: caller is responsible for deleting the created temporary
        directory.
        """
        if None is self._tempdir or not os.path.isdir(self._tempdir):
            self._tempdir = tempfile.mkdtemp()
        return self._tempdir

    @property
    def source(self):
        """
        The source file name.  It is the same as :py:attr:`sourcebase`.

        >>> Filename(source='dir1/name.tex', dest='dir2/', ftype='png').source
        'name.tex'
        """
        return self.sourcebase

    @property
    def dest(self):
        """
        The destination file name.

        >>> Filename(source='dir1/name.tex', dest='dir2/', ftype='png').dest
        'name.png'
        >>> Filename(source='dir1/name.tex', dest='dir2/', ftype='eps').dest
        'name.eps'
        """
        return '.'.join([self.destmain, self.destext])

    @property
    def sourcepath(self):
        """
        The absolute path to the source file.
        """
        return os.path.join(self.sourcedirabs, self.source)

    @property
    def destpath(self):
        """
        The absolute path to the destination file.
        """
        return os.path.join(self.destdirabs, self.dest)

    @property
    def sourceext(self):
        """
        Extension part of the base name of the destination file.
        """
        return "tex"

    @property
    def ftype(self):
        """
        Type of the destination file.
        
        It should be the same as :py:attr:`destext`.

        >>> Filename(source='dir1/name.tex', dest='name.png').ftype
        'png'
        """
        return self.destext

    @property
    def intertex(self):
        """
        The intermediate TEX file name for :py:meth:`Pstricks.pst`.

        >>> Filename(source='dir1/name.tex', ftype='png').intertex
        'name.tex'
        >>> Filename(source='dir1/name.tex', dest='dir2/other.png').intertex
        'other.tex'
        """
        return '.'.join([self.destmain, 'tex'])

    @property
    def intereps(self):
        """
        The intermediate EPS file name for :py:meth:`Pstricks.pst`.

        >>> Filename(source='dir1/name.tex', ftype='png').intereps
        'name.eps'
        >>> Filename(source='dir1/name.tex', dest='dir2/other.png').intereps
        'other.eps'
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
    parser.add_argument('--font', dest='font', action='store',
                        default=None, choices=[None, 'cmbright'],
                        help='font selection (default = %(default)s)')
    parser.add_argument('-k', dest='keep_tmp', action='store_true',
                        default=False,
                        help='keep temporary directory')
    parser.add_argument('-t', dest='dstext', type=str, action='store',
                        default='png',
                        help='destination file type '
                             '(default = %(default)s)')
    parser.add_argument('-v', '--verbose', dest='verbosity', action='store',
                        type=int, default=3,
                        help='verbosity of output (1-5) '
                             '(default = %(default)d)') # FIXME: not used.
    parser.add_argument('--tempdir', dest='tempdir', action='store',
                        default=None,
                        help='DANGEROUS! Be sure to set -k, '
                        'otherwise the temporary directory you specified '
                        'will be deleted after the script ends.')
    args = parser.parse_args()

    runner = Pstricks(**vars(args))
    fn = Filename(source=args.src, dest=args.dst, ftype=args.dstext,
                  tempdir=args.tempdir)
    runner(fn, **vars(args))

    return 0


if __name__ == '__main__':
    main()
