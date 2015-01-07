"""Command line use of pyjoint

To run pyjoint from the command line do the following:

    python -m pyjoint ...

Use the option --help for more information.

"""

import argparse
import textwrap
from pyjoint.__version__ import VERSION


def parse_options():
    """Interpret the command line inputs and options. """
    desc = """
pyjoint computes the miter and tilt angles of polyhedron faces.

"""
    ver = "pyjoint %s" % VERSION
    epi = """

more info:
  http://jmlopez-rod.github.com/pyjoint

version:
  pyjoint %s

""" % VERSION
    raw = argparse.RawDescriptionHelpFormatter
    argp = argparse.ArgumentParser(formatter_class=raw, version=ver,
                                   description=textwrap.dedent(desc),
                                   epilog=textwrap.dedent(epi))
    argp.add_argument('inputfile', type=str,
                      help='input file to process')

    return argp.parse_args()


def run():
    """Run pyjoint from the command line. """
    arg = parse_options()
    print arg


if __name__ == '__main__':
    run()
