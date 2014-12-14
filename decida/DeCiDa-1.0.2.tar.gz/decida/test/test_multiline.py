#!/usr/bin/env python
import user, decida, decida.test
from decida.readfile2list import readfile2list

test_dir = decida.test.test_dir()
lines = readfile2list(test_dir + "TextWindow.txt")

for line in lines :
    for uline in decida.multiline(line, 20) :
        print uline
