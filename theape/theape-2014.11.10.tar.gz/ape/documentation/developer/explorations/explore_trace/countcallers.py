
from trace import Trace
from test_class import TestExec


t = TestExec()
trace = Trace(countcallers=1)
try:
    trace.run('t.run_this_and_that()')
    print "COUNTCALLERS"
except NameError:
    print NameError
