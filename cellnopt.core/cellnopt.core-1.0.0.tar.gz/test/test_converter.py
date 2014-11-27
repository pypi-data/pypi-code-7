from cellnopt.core import *
from tools import *


def test_converter():
    c = Interactions()
    assert c.reacID == []
    assert c.specID == []
    assert c.namesSpecies == []
    c.add_reaction("A=B")
    print c


def test_converter_from_sif():
    s = SIF(simple)
    #assert c.reacID == ['', '','']
    assert s.specID == s.namesSpecies

def test_wrong_reactions():
    c = Interactions()
    try:
        c.add_reaction("A")
        assert False
    except:
        assert True
    for symbol in c.valid_symbols:
        try:
            c.add_reaction("A=%sB" % symbol)
            assert False
        except:
            assert True

def test_search():
    c = Interactions()
    c.add_reaction("MEK=ERK")
    c.search("MEK", verbose=True)
    c.search("ME", strict=True, verbose=True)
    c.search("MEK", strict=True, verbose=True)


def test_remove_species():
    c = Interactions()
    c.add_reaction("A+B=C")
    c.remove_species("A")
    c.reacID == ['B=C']


    c.add_reaction("A=C")
    c.remove_reaction("A=C")
    c.reacID == ['B=C']

    # no effect
    c.remove_species("dummy")

    # should be empty after this
    c.remove_species(["A", "B", "C"])
    assert len(c.reacID) == 0

    c.add_reaction("A=B")
    c.remove_species("A")

    # wrong type
    try:
        c.remove_species(1)
        assert False
    except:
        assert True


