#!/usr/bin/env python

from pystats import *

with open('data.txt') as f:
    res = stats(stream = f, field=1, delimiter=' ', skip = 0, confidence=0.95)
    print res