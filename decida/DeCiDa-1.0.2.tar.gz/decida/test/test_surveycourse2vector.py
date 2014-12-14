#!/usr/bin/env python
########################################################################
# NAME    : test_surveycourse2vector
# PURPOSE : decida test
# AUTHOR  : Richard Booth
# DATE    : Fri Nov  1 19:29:24 2013
########################################################################
import user, decida
from decida.Data    import Data   
from decida.XYplotx import XYplotx
from decida.surveycourse2vector import surveycourse2vector
courses = [
    "deed1",
    "N45.58.37E:118.03",
    "-N39.47.37W:56.69",
    "-N87.20.37W:192.13",
    "S34.12.52E:175.85",
    "S82.08.17E:249.09",
    "S27.40.00E:860.42",
    "S68.52.38W:451.81",
    "N40.21.00W:305.53",
    "S67.08.00W:660.17",
    "N23.44.41W:479.33",
    "N86.28.28E:340.91",
    "N05.09.17E:285.58",
    "N08.14.59E:346.35",
    "N77.43.43W:54.52",
    "N45.58.37E:118.03",
]
title = courses.pop(0)
xdata = []
ydata = []
x, y = 0.0, 0.0
xdata.append(x)
ydata.append(y)
for course in courses :
    dx, dy = surveycourse2vector(course)
    x += dx
    y += dy
    xdata.append(x)
    ydata.append(y)
d = Data()
d.read_inline("x", xdata, title, ydata)
command=(d, "x %s" % (title))
XYplotx(command=command, traces=["both"], xtitle="", ytitle="",
    xmin=-600, xmax=1100, ymin=-1150, ymax=100)
