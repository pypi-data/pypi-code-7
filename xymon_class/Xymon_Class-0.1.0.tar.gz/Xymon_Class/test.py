#!/usr/bin/python
# -*- coding: utf-8 -*-

from Xymon import Xymon

xymon = Xymon(debug=1)

xymon.print_line("GREEN ADDITIONAL TEXT COLORED")
xymon.print_line("ADDITIONAL TEXT")

# xymon.print_it()
xymon.send()


xymon_data = Xymon(my_type="data")
xymon.print_line("GREEN ADDITIONAL TEXT COLORED")
