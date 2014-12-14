#!/usr/bin/env python
import sys, os.path

def test_dir() :
    for d in sys.path :
        file = "%s/decida/test/test_dir.py" % (d)
        if os.path.isfile(file) :
            return(d + "/decida/test/")
    print "can't locate decida test directory"
    exit()
