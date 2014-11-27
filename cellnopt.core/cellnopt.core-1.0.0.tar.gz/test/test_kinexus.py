from cellnopt.core.io.kinexus import Kinexus
from easydev import get_share_file
import os
filename = get_share_file("cellnopt.core", "data", "kinetic.csv")

def _test_kinexus():
    k = Kinexus(filename)
    k.data
    k.get_name_from_uniprot("P43403", taxon=9606) == "ZAP70"
    k.select_globally_normalised()
    k.export2midas(uniprot=False)

