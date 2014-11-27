from cno import cnodata, CNOGraph, XMIDAS
from cno.milp import MILPTrain


def test_milp():

    filename_pkn = cnodata("PKN-ToyMMB.sif")
    filename_midas = cnodata("MD-ToyMMB.csv")
    pkn = CNOGraph(filename_pkn, filename_midas)
    midas = pkn.midas
    pkn.compress()
    pkn.expand_and_gates()
    model = cno.milp.model.MILPTrain(pkn, midas)
    model.train()
    #model.get_rxn_solution()
