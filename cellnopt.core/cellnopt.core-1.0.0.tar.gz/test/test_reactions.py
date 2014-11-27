from cellnopt.core import *
import numpy
import tempfile
import os

from easydev import gsf


def test_reaction():
   a = Reactions(gsf("cellnopt.core", "data", 'reactions'))
   assert len(a.reacID) == 123
   assert len(a.specID) == 94
   #assert a.notMat.sum().sum() == 31
   #assert a.interMat.sum().sum() == -52

   f = tempfile.NamedTemporaryFile()
   a.writeSIF(f.name)


   f = tempfile.NamedTemporaryFile()
   a.writeSIF(f.name)


def test1():
    r = Reactions()
    r.add_reaction("a+b=g")
    r.add_reaction("a+b=c")
    assert r.specID ==  ['a', 'b', 'c', 'g']

    assert sorted(r.namesSpecies) == sorted(r.specID)

    r.writeSIF("test.sif")  # this creates the nodes attributes that change behabour of specID
    r.remove_reaction("a+b=c")
    assert r.specID ==  ['a', 'b', 'g']
    os.remove("test.sif")
