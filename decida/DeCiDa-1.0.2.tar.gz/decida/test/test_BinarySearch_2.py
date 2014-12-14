#!/usr/bin/env python
import user, decida, math
from decida.BinarySearch import BinarySearch

def funct(x) :
    a, b, c = 1.0, -4.0, 2.0
    y = a*x*x + b*x + c
    return y

bin = BinarySearch(
     low=1.0, high=2.0, min=-10, max=3,
     min_delta=1e-6, bracket_step=0.1
)

bin.start()
while not bin.is_done() :
    x=bin.value()
    f=funct(x)
    success = (f >= 0)
    print "%-10s: x=%-18s y=%-18s %-5s" % (bin.mode(), x, f, success)
    bin.update(success)

print
print "x = ", bin.last_success()
