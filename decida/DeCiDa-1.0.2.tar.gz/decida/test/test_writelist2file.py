#!/usr/bin/env python
import user, decida
from decida.writelist2file import writelist2file

lines = ["line1", "line2"]

writelist2file(lines, "test_writelist2file.txt")
