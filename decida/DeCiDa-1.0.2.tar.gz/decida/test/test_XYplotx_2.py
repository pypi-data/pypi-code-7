#!/usr/bin/env python
import user, decida, math
from decida.Data import Data
from decida.XYplotx import XYplotx

d = Data()
npts, xmin, xmax = 10000, 0, 10
x_data = decida.range_sample(xmin, xmax, num=npts)
y_data = []
for x in x_data :
    y_data.append(math.sin(x*10))
d.read_inline("X", x_data, "Y", y_data)
XYplotx(command=[d, "X Y"])
