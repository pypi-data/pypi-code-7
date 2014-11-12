#!/usr/bin/python
# -*- coding: UTF-8 -*-

spark_chars = u" ▁▂▃▅▆▇"

def sparkprob(series, minimum=0.0, maximum=1.0):
    # Assumed between 0 and 1 for a probability distribution
    series = [ (float(i)-minimum)/(maximum-minimum) for i in series ]
    return (u' '.join([spark_chars[int(round(x * (len(spark_chars) - 1.0)))] for x in series])).encode("utf-8")
