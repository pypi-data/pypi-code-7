#!/usr/bin/env python
import user, decida, decida.test
from decida.TextWindow import TextWindow

test_dir = decida.test.test_dir()
file = test_dir + "TextWindow.txt"
twin = TextWindow(text_height=30, wait=False)
twin.fileread(file)
twin["text_width"]  = 90
twin.wait("continue")
twin.clear()
twin.wait()
