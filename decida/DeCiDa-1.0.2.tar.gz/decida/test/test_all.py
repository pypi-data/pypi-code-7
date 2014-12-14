#!/usr/bin/env python
import sys, os, decida.test

tests = decida.test.test_list()
for test in tests :
    print " ... %s ... " % (test)
    exec("import decida.test.%s" % (test))
