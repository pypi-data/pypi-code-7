# -*- coding: utf-8 -*-
"""
====================================================
pykit-sci: python package for science (:mod:`pksci`)
====================================================

Documentation is available online at `pksci_doc`_.

.. _pksci_doc: http://projects.geekspin.net/pksci/doc

Contents
--------
pykit-sci provides the following sub-packages.

Sub-packages
------------

::

 chemistry           --- chemistry package
 electronics         --- electronics package
 nanosci             --- nano-science package
 physics             --- physics package
 scripts             --- scripts for running command-line tools
 tools               --- misc tools

::

 __version__   --- pykit-sci version string

"""
from __future__ import absolute_import, division, print_function

__all__ = ['chemistry',
           'electronics',
           'nanosci',
           'physics',
           'scripts',
           'tools']

from pksci.version import version as __version__
