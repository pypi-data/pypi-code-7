
from zio import *

io = zio('python2 cat_with_sighup.py')
io.writeline('asdf')
io.readline()

io = zio('python2 cat_with_sighup.py')
io.writeline('asdf')
io.readline()

io = zio('python2 cat_with_sighup.py')
io.writeline('asdf')
io.readline()
