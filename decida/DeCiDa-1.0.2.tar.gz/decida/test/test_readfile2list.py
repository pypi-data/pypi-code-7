#!/usr/bin/env python
import user, decida, decida.test
from decida.readfile2list import readfile2list

test_dir = decida.test.test_dir()
for line in readfile2list(test_dir + "TextWindow.txt") :
    print line
