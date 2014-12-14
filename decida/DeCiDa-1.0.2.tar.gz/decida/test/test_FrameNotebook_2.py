#!/usr/bin/env python
import user, decida, decida.test
from decida.Data          import Data
from decida.DataViewx     import DataViewx    
from decida.FrameNotebook import FrameNotebook

test_dir = decida.test.test_dir()
files = ("icp_tr.report", "icp_tr.report")

fn = FrameNotebook(tab_location="right")
for file in files :
    d = Data()
    d.read(test_dir + file)
    plt = "dt icp_final icp_expt"
    DataViewx(fn.new_page(file), data=d, command=[[plt]])
    fn.wait("continue")
