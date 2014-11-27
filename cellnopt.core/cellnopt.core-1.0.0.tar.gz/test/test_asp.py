from cellnopt.core import *

import unittest
from tools import net as net_sample


class NetTest(unittest.TestCase):
    def setUp(self):
        self.n = NET(net_sample)

    def test_add(self):
        n = NET()
        n.add_net("a -> b +")
        n.add_net("a -> c -")

    def test_bad_file(self):
        try:
            n = NET("dummy")
            assert False
        except:
            assert True

    def test_print(self):
        print(self.n)

    def test_write2sif(self):
        import tempfile
        f = tempfile.NamedTemporaryFile()
        self.n.write2sif(f.name)
        f.close()

    def test_wrong_net(self):
        try:
            self.n.add_net("dummy")
            assert False
        except:
            assert True

    def test_wrong_net(self):
        try:
            self.n.add_net("A -> B+")
            assert False
        except:
            assert True




def test_net2reaction():
    assert net2reaction("A -> B +") == "A=B"
    assert net2reaction("A -> B -") == "!A=B"


