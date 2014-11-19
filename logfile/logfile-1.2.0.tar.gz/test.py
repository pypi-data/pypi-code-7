#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import doctest
import unittest

#
# Test Runner
# ------------------------------------------------------------------------------
#

# support for `python setup.py test`
suite = doctest.DocFileSuite("README.md") 

if __name__ == "__main__":
    doctest.testfile("README.md")

