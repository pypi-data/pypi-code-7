import networkx as nx
from cellnopt.core import *


"""

on the PKN-ToyMMB.sif model (and data), an optimisation in cno gives
after preprocessing ,this besst bitstirng

model$reacID
 [1] "Raf=Mek"        "PI3K=Akt"       "Mek=p90RSK"     "Mek=Erk"       
 [5] "!Akt=Mek"       "TNFa=PI3K"      "Jnk=cJun"       "Erk=Hsp27"     
 [9] "EGF=PI3K"       "TNFa=Jnk"       "TNFa=NFkB"      "TNFa=Hsp27"    
[13] "EGF=Raf"        "TNFa+EGF=PI3K"  "Raf+!Akt=Mek"   "Erk+TNFa=Hsp27"


res$bString
 [1] 1 1 1 1 0 1 0 0 1 0 1 1 1 0 0 0
 
the mapback gives
# (model, pknmodel, res$bString))
 [1] 1 1 1 1 0 1 0 0 1 0 1 1 1 0 0 0

[1] "showing red link even if empty"
> pknmodel$reacID
 [1] "Raf=Mek"    "TRAF6=Jnk"  "TRAF6=p38"  "TRAF6=NFkB" "PI3K=Akt"  
 [6] "Mek=p90RSK" "Mek=Erk"    "!Akt=Mek"   "p38=Hsp27"  "TNFa=TRAF6"
[11] "TNFa=PI3K"  "Jnk=cJun"   "Erk=Hsp27"  "EGF=Ras"    "EGF=PI3K"  
[16] "Ras=Raf"   




"""



def search_path(G, source, target):
    """Search all simple paths in the graph G from source to target
    
    :param G:
    :param source:
    :param target:
    :return: list of edges
    """
    try:
        return list(nx.all_simple_paths(G, source, target))
    except:
        print(source + " " + target)


def mapback(pknmodel, submodel, edges2map):
    """
    :param list edges2map: list of edges 2 map. an ed ge is a tuple as returned by G.edges()
    pknmodel and model are 2 cnographs

    :return: list of edges

    bString should be a list of edges ()


    #the mapback for each link A->B in the compressed model is done looking
    #at the PKN as a graph and considering a subgraph of it including only
    #node A, node B and compressed nodes. All paths going from A to B in this
    #subnetwork are marked as active in the PKN.

    ::

        >>> c1 = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
        >>> c2 = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
        >>> c2.preprocessing()
        >>> newedges = mapback.mapback(c1,c2,edges)
        >>> c3 = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
        >>> for edge in c3.edges():
        ...     if edge not in newedges:
        ...         c3.remove_edge(edge[0], edge[1])
        >>> c3.plotdot()




    .. todo:: current issue is nonc not being linked

    :reference: mapBack.R from CellNOptR
    """
    #assert no ands in pknmodel
    edges1 = sorted(pknmodel.edges())
    edges2 = sorted(pknmodel.edges())

    links2map = edges2map 
    bStringPKN = [0] * len(pknmodel.edges())

    #may not be required
    nonc = pknmodel.findnonc()

    #compressed = pknmodel.

    newedges = []
    # for each link 2 map in the submodel
    for edge in links2map:
        endNode = edge[1]
        if "=" in endNode:
            endNode = endNode.split("=")[1]
        endNode = endNode.replace("!", "")
        startNodes = edge[0] # may be an AND node

        # what about endNode with and gates ??
        for startNode in startNodes.split("=")[0].split("^"):
            startNode = startNode.replace("!", "")
            # consider subgraph with startnode,end node and compressed nodes
            okNodes = submodel._compressed + nonc + [endNode, startNode]
            noNodes = [n for n in pknmodel.nodes() if n not in okNodes]
            #here is the subgrqph
            gg = pknmodel.copy()
            gg.remove_nodes_from(noNodes)

            # seqrch this sugrqph for paths between startnode and endnode
            paths = search_path(gg, startNode, endNode)
            if paths == None:
                print("FIXME any issue with the AND gates ???")
                print("no path between {} and {}".format(startNode, endNode))
            else:
                for path in paths:
                    for j2 in range(1, len((path))):
                        n1 = path[j2-1]
                        n2 = path[j2]
                        reacPKN = n1 + "=" + n2
                        newedges.append(reacPKN)

    newedges = set(newedges)
    newedges = [tuple(x.split("=")) for x in newedges]
    return newedges

"""

    # example
    c1 = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
    c2 = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
    c2.preprocessing()
    edges = [e for e in c2.edges() if "^" not in e[0] and "^" not in e[1] and e not in [("map3k1", "ap1")]


     for edge in c3.edges():
         if edge not in newedges:
            c3.remove_edge(edge[0], edge[1])

"""


"""
pknmodel$reacID
 [1] "p90rsk=creb"  "rac=map3k1"   "nik=ikk"      "!ikk=ikb"     "mkk4=p38"    
  [6] "mkk7=jnk"     "map3k7=mkk4"  "map3k7=nik"   "jnk=cjun"     "tnfr=pi3k"   
  [11] "tnfr=traf2"   "traf2=map3k7" "egfr=sos"     "egfr=pi3k"    "pi3k=rac"    
  [16] "pi3k=akt"     "!ph=sos"      "ex=ikb"       "!ikb=nfkb"    "mek=p90rsk"  
  [21] "mek=erk"      "erk=ph"       "ras=map3k1"   "ras=raf1"     "map3k1=mkk4" 
  [26] "map3k1=mkk7"  "raf1=mek"     "tnfa=tnfr"    "!akt=gsk3"    "egf=egfr"    
  [31] "nfkb=ex"      "cjun=ap1"     "sos=ras"     
  > bmodel
   [1] 0 1 1 1 1 0 1 1 0 1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 0 1 1 1 1 1 0 1

> model$reacID
    [1] "!ikb=nfkb"       "pi3k=map3k1"     "map3k1=p38"      "tnfa=pi3k"      
     [5] "!tnfa=ikb"       "tnfa=p38"        "egf=sos"         "egf=pi3k"       
      [9] "!erk=sos"        "nfkb=ikb"        "raf1=erk"        "sos=map3k1"     
      [13] "sos=raf1"        "!pi3k=gsk3"      "map3k1=ap1"      "tnfa+egf=pi3k"  
      [17] "!tnfa+nfkb=ikb"  "pi3k+sos=map3k1" "egf+!erk=sos"    "map3k1+tnfa=p38"
      > bs
       [1] 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0
"""


"""      # can contain more than 1 element in case of AND nodes

        for (j1 in 1:length(PathOK)){
          for (j2 in 2:length(PathOK[[j1]])){
            node1<-PathOK[[j1]][j2-1]
            node2<-PathOK[[j1]][j2]
            reacPKN<-paste(node1,node2,sep="=")
            bStringPKN[grep(reacPKN,PKN$reacID)]<-1
          }
        }

      }
    }

"""  
  
def get_test_graphs():
    c = CNOGraph()
    c.add_reaction("A+B=C")
    c.add_reaction("C=dummy")
    c.add_reaction("dummy=D")
    c._stimuli = ["A", "B"]
    c._signals = ["C", "D"]

    c2 = c.copy()
    c2.preprocessing()
    edges2map = [("A","C"), ("C", "D")]

    return (c, c2, edges2map)


