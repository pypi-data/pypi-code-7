from cellnopt.core import ADJ2SIF, SIF, get_share_file, CNOGraph
import os

from  tempfile import mkstemp

def test_adj2sif():



    f1 = get_share_file("adjacency_matrix.csv")
    f2 = get_share_file("adjacency_names.csv")

    s = ADJ2SIF(f1, f2)
    s.export2sif()

    fd, name = mkstemp(suffix=".sif")
    print name
    s.export2sif(name)
    s2 = SIF(name)
    s2.nodes1 == ["A", "A"]
    s2.nodes2 == ["B", "C"]
    s2.edges == ["1", "1"]

    c = CNOGraph(s.G)

def test_load():
    a = ADJ2SIF()
    f1 = get_share_file("adjacency_matrix.csv")
    f2 = get_share_file("adjacency_names.csv")
    a.load_adjacency(f1)
    a.load_names(f2)
    CNOGraph(a.G) # just to check that it can be imported via cnograph

