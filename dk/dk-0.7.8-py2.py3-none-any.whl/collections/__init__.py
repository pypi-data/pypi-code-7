# -*- coding: utf-8 -*-

"""Abstract Data Types -- mostly record types with different semantics.
"""
# pylint:disable=W0611
from __future__ import absolute_import

from .mmap import mmap
from .pset import pset, record, defset
from .sdict import sdict
from .OrderedSet import oset
from .invdict import invdict
from .xmlrec import xmlrec
