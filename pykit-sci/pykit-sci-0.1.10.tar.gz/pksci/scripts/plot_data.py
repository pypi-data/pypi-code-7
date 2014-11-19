# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
=====================================================
Command line script (:mod:`pksci.scripts.plot_data`)
=====================================================

Plot data.

.. currentmodule:: pksci.scripts.plot_data

.. argparse::
   :module: pksci.scripts.plot_data
   :func: argparser
   :prog: plot_data

"""
from __future__ import absolute_import, division, print_function
__docformat__ = 'restructuredtext en'

import sys

from ..tools.mpltools import plot_argparser, \
    XYPlotConfigParser, XYPlotGenerator


def argparser():
    parser = plot_argparser()
    return parser


def main():
    plotcfgparser = XYPlotConfigParser(argparser=argparser())
    XYPlotGenerator(datasets=plotcfgparser.datasets,
                    plotconfig=plotcfgparser.config,
                    autoplot=True)

if __name__ == '__main__':
    sys.exit(main())
