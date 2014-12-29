# -*- coding: utf-8 -*-
"""Implementation of pyprof2html commands.
"""

from optparse import OptionParser
import pyprof2html
from pyprof2html.core import Converter
from pyprof2html.environment import ENVIRON

__all__ = ['pyprof2html_main']


def pyprof2html_main():
    """execute a script of pyprof2html"""
    parser = OptionParser(version="pyprof2html %s" % (pyprof2html.__version__),
                          usage="Usage: pyprof2html [options] PROFILE_DATA")
    parser.add_option('-r', '--raw', action='store_true',
                      help='raw print mode')
    parser.add_option('-x', '--xhtml', action='store_true',
                      help='html print mode (default)')
    parser.add_option('-t', '--template', dest='template_file',
                      help='jinja2 template file')
    parser.add_option('-n', '--num', type='int', dest='print_functions',
                      default=20, help='print to N funcs.(default 20)')
    parser.add_option('-o', '--output-dir', dest='output_dir', default='html',
                      help='output HTML under the this directory.' \
                           '(default: html)')
    opts, args = parser.parse_args()
    if not len(args):
        print(parser.format_help())
        return 1
    p2h = Converter(args[0])
    p2h.functions_number = opts.print_functions
    if opts.template_file:
        p2h.tmpl = ENVIRON.get_template(open(opts.template_file).read())
    if opts.raw:
        outmode = 'raw'
    elif opts.xhtml:
        outmode = 'html'
    else:
        outmode = 'html'
    p2h.printout(outmode, opts.output_dir)
    if outmode == 'html' and p2h.profiledata_count > 20:
        p2h = Converter(args[0])
        p2h.printout(filetype=outmode,
                     output_directory=opts.output_dir,
                     output_htmlfile='index-all.html',
                     functions_number=99999)
    return 0
