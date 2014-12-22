
# python standard library
from trace import Trace

from test_class import TestExec


trace = Trace()
t = TestExec()
try:
    trace.runfunc(t.run_this_and_that)
except NameError:
    print NameError  


def args_func(a, b, c=3):
    print 'a',a
    print 'b',b
    print 'c',c

trace.runfunc(args_func, 1, b=2)
