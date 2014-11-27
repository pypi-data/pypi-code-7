from cellnopt.core.oldmidas import *
from cellnopt.core.makecnolist import *
from cellnopt.data import cnodata


class TestCNOList():
    def __init__(self):

        self.m = MIDASReader(cnodata('MD-ToyMMB.csv'))


    def test_cnolist(self):
        self.m.cnolist
        self.m.cnolist.plot_exp()
        self.m.cnolist.residualErrors 
        self.m.cnolist.pcolor()

    def _test_cnolist_plot_exp(self):
        self.m.cnolist.plot_exp()

    def test_print(self):
        print self.m.cnolist
