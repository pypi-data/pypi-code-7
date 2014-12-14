#!/usr/bin/env python
import user, decida, math
from decida.BinarySearch import BinarySearch

def funct(x) :
    y = math.log(x) - 1.0
    return y

bin = BinarySearch(
     low=0.5, high=2.0, min=0.1, max=10,
     min_delta=1e-6, bracket_step=0.1, find_max=False
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
