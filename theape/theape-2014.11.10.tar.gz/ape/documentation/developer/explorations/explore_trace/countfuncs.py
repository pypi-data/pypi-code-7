
from trace import Trace
from test_class import TestExec


t = TestExec()
trace = Trace(countfuncs=True)
try:
    trace.run('t.run_this_and_that()')
    print "COUNTFUNCS"
except NameError:
    print NameError
