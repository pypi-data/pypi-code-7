#!/usr/bin/env python
import user, decida

args = ["-h", "-test", "test1", "datafile"]
file = "default_file"
test = "default_test"
while len(args) > 0 :
    arg = decida.lshift(args)
    if   arg == "-h" :
        print "help"
    elif arg == "-test" :
        test = decida.lshift(args)
    else :
        file = arg

print "test = ", test
print "file = ", file
