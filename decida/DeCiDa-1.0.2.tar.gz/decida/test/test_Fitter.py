#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.Fitter import Fitter
from decida.DataViewx import DataViewx

test_dir = decida.test.test_dir()

d=Data()
d.read(test_dir + "icp_tr_diff.report")
ftr=Fitter(
    """
        dicp_mod = a0 + a1*sign(dt)*(1-(1+(abs(dt/u0))^x0)/(1+(abs(dt/u1))^x1))
    """,
    """
        a0 0       include lower_limit=-1   upper_limit=1
        a1 6e-3    include lower_limit=1e-8 upper_limit=1
        u0 2.3e-10 include lower_limit=1e-12
        u1 2.3e-10 include lower_limit=1e-12
        x0 1.05    include lower_limit=1
        x1 1.05    include lower_limit=1
    """,
    meast_col="dicp",
    model_col="dicp_mod",
    error_col="residual",
    residual="relative",
    data=d
)
ftr.fit()

print ftr.par_values()

DataViewx(data=d, command=[["dt residual"], ["dt dicp dicp_mod"]])
