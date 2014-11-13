#!/usr/bin/env python3
import pybufr_ecmwf.ecmwfbufr
import numpy
data = pybufr_ecmwf.ecmwfbufr.retrieve_settings()
print(data)
