
# python standard library
from trace import Trace

from test_class import TestExec


t = TestExec()
exec('t.run_this()')


trace = Trace()
try:
    trace.run('t.run_this_and_that()')
    print 'END_DEFAULT'
except NameError:
    print NameError  
