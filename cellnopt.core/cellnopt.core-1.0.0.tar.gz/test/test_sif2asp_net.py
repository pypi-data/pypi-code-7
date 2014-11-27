from cellnopt.core import sif2asp
import easydev
import os

cleanup = "PKN-ToyMMB.net"

def test_sif2aspnet_py():
    filename = "PKN-ToyMMB.sif"
    model = easydev.get_share_file("cellnopt.core", "data", filename)
    c = sif2asp.SIF2ASP(model)
    c.write2net(filename.replace(".sif", ".net"))
    os.remove(cleanup) 
    print(c)

