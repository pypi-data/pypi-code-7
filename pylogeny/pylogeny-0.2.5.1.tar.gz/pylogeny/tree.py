''' Container definition for (phylogenetic) bifurcating or multifurcating trees defined using Newick strings. '''

# Date:   Oct 20 2014
# Author: Alex Safatli
# E-mail: safatli@cs.dal.ca

# Imports

import newick, rearrangement
from math import factorial as fact
from numpy import median

# Function Defitions

numberRootedTrees   = lambda t: numberUnrootedTrees(t+1)
numberUnrootedTrees = lambda t: (fact(2*(t-1)-3))/((2**(t-3))*fact(t-3))

# Class Definitions for Trees

class tree(object): # TODO: Integrate with P4 Tree class (?).
    
    ''' Defines a single (phylogenetic) tree by newick string;
    can possess other metadata. '''
    
    def __init__(self,newi='',check=False):
        
        ''' If enabled, "check" will force the structure to reroot
        the given Newick string tree to a lowest-order leaf in order
        to ensure a consistent Newick string among any duplicate
        topologies. '''
        
        self.name   = ''
        self.score  = None
        self.origin = None
        self.newick = newi
        if (check): self._checkNewick(newi)        
        else:       self.setNewick(newi)
    
    # Getters, Mutators
    
    def getName(self):     return self.name
    def setName(self,n):   self.name = n
    def getScore(self):    return self.score
    def setScore(self,s):  self.score = s
    
    def getOrigin(self):   return self.origin
    def setOrigin(self,o):
        
        ''' Set the "origin" or specification of where this tree
        was acquired or constructed from; a string. '''
        
        self.origin = o    
        
    def getNewick(self):   return self.newick
    def setNewick(self,n):
        
        ''' Set Newick string to n; also reacquires corresponding
        "structure" or Newick string without branch lengths. '''
        
        self.newick = n
        self.struct = self._getStructure()   
        
    def getStructure(self):
        
        ''' Returns "structure", a Newick string without branch lengths. '''
        return self.struct 
    
    def getSimpleNewick(self):

        ''' Return a Newick string with all taxa name replaced with
        successive integers. '''
    
        o = newick.parser(self.newick).parse()
        n = newick.getAllLeaves(o)
        for _ in xrange(1,len(n)+1): n[_].label = str(_)
        return str(o) + ';'        
    
    # Other Functionality
    
    def toTopology(self):
        
        ''' Return a rearrangement.topology instance for this tree to allow for 
        rearrangement of the actual structure of the tree. '''
        
        t = rearrangement.topology()
        t.fromNewick(self.newick)
        return t
    
    # Internals
        
    def __eq__(self,o): return (o.struct == self.struct)
    def __ne__(self,o): return not (self.__eq__(o))
    def __str__(self): return self.newick
    
    def _checkNewick(self,newi):
        
        ''' PRIVATE: Run the Newick string through a 
        parse pass and reroot to lowest-order leaf in
        order to ensure a consistent Newick string. '''
        
        newi        = newi.strip('\n').strip(';') + ';'   
        prsd        = newick.parser(newi).parse()
        self.newick = rearrangement.topology(prsd).toNewick()
        self.struct = self._getStructure(prsd)
    
    def _getStructure(self,prsd=None):
        
        ''' PRIVATE: Acquires a newick string without any
        defined branch lengths. '''
        
        if prsd: p = prsd
        else: p = newick.parser(self.newick).parse()    
        newick.removeBranchLengths(p)
        return str(p) + ';'  
    
class treeSet(object):
    
    ''' Represents an ordered, unorganized collection of trees 
    that do not necessarily comprise a combinatorial space. '''
    
    def __init__(self):
       
        self.trees = list()    
    
    def addTree(self,tr): 

        ''' Add a tree object to the collection. '''
    
        self.trees.append(tr)

    def addTreeByNewick(self,newick):
        
        ''' Add a tree to the structure by Newick string. '''
        
        t = tree(newick)
        self.addTree(t)    
        
    def removeTree(self,tr):
        
        ''' Remove a tree object from the collection if present. '''
        
        if tr in self.trees:
            self.trees.remove(tr)
    
    def indexOf(self,tr):
        
        ''' Acquire the index in this collection of a tree object. 
        Returns -1 if not found. '''
        
        if tr in self.trees: return self.trees.index(tr)
        else: return -1
    
    def __getitem__(self,i): return self.trees[i]
    
    def toTreeFile(self,fout):
        
        ''' Output this landscape as a series of trees, separated by
        newlines, as a text file saved at the given path. '''        
        
        o = open(fout,'w')
        o.write(str(self))
        o.close()
        return fout
        
    def __str__(self):
        return '\n'.join([t.getNewick() for t in self.trees])
    
# Bipartition Class Definitions    
    
''' Using the term borrowed from nomenclature of a bipartite graph, a bipartition for a phylogenetic tree coincides with the definition of two disjoint sets U and V . A branch in a phylogenetic tree defines a single bipartition that divides the tree into two disjoint sets U and V . The set U comprises all of the children leaf of the subtree associated with that branch. The set V contains the rest of the leaves or taxa in the tree. This package handle operations involving the representation of tree bipartitions. '''

class bipartition(object):

    ''' A tree bipartition. Requires a tree topology. '''

    def __init__(self,topol,bra=None):
        self.topology = topol
        self.branch   = bra
        self.btuple   = None # Tuple list representation.
        self.strrep   = None # String representation
        self.shortstr = ''   # Shorter string representation
        self.shortmap = None # Shorter string mapping of taxa to symbols
        self.reconfis = None # Possible reconfigurations as rearrangement objects.
        self._getStringRepresentation()
        self._getShortStringRepresentation()
        self._getBranchListRepresentation()
    
    def __hash__(self): return hash(self.shortstr)
    
    def __eq__(self,o):
        
        if (type(o) != bipartition): return False
        l,r   = self.strrep
        lo,ro = o.strrep
        return ((lo==l and ro==r) or (ro==l and lo==r))
    
    def __ne__(self,o): return not self.__eq__(o)
    
    def _getStringRepresentation(self):
        
        ''' PRIVATE: Obtain string representation of a branch in a topology. '''
        
        if (self.branch == None): return
        if (self.topology == None):
            raise ValueError('Topology does not exist or is equal to None.')
        z            = self.topology.getStrBipartitionFromBranch(self.branch)
        l,r          = sorted(z[0]),sorted(z[1])
        self.strrep  = (l,r)
        
    def _getShortStringRepresentation(self):
        
        ''' PRIVATE: Obtain short string representation of branch/bipartition. '''
        
        ind  = 65 # 'A'
        l,r  = self.strrep
        x    = max((l,r),key=lambda d:len(d))
        if x == l: y = r
        else: y = l
        l,r  = x,y
        o    = ''
        lbls = [x for x in l] + [x for x in r]
        lblm = {}
        lbls = sorted(lbls) # Sort them.
        for i in lbls:
            lblm[i] = chr(ind)
            ind += 1
        for i in l: o += lblm[i]
        o += ':'
        for i in r: o += lblm[i]
        self.shortstr = o
        self.shortmap = lblm
        
    def _getBranchListRepresentation(self):
        
        l = [self.branch] + newick.getAllBranches(self.branch)
        r = [branch for branch in self.topology.getBranches(
            ) if not branch in l]
        self.btuple = (l,r)       
        
    def _getBranchFromString(self):
        
        ''' PRIVATE: Obtain branch information from a string representation. '''
        
        if not self.strrep or type(self.strrep) != tuple:
            raise IOError('Could not read string representation of bipartition.')
        self.branch = self.topology.getBranchFromStrBipartition(self.strrep)
        
    def _makeSPRRearrangements(self):
        
        ''' PRIVATE: Perform possible rearrangements. '''
        
        self.reconfis = self.topology.allSPRForBranch(self.branch)

    def fromStringRepresentation(self,st):
        
        ''' Acquire all component elements from a string representation 
        of a bipartition. '''
        
        self.strrep = st
        self._getBranchFromString()
        self._getShortStringRepresentation()
        
    def getBranch(self):
        
        ''' Get branch corresponding to this bipartition. '''
        
        return self.branch
    
    def getStringRepresentation(self):
        
        ''' Get the string representation corresponding to this bipartition. '''
        
        return self.strrep
    
    def getShortStringRepresentation(self):
        
        ''' Get the shorter string representation corresponding to this bipartition. '''
        
        return self.shortstr
    
    def getShortStringMappings(self):
        
        ''' Get the mapping of symbols from taxa names for the shorter string representation. '''
        
        return self.shortmap
    
    def getBranchListRepresentation(self):
        
        ''' Get the tuple of lists of branches that represent this bipartition. '''
        
        return self.btuple
    
    def getSPRRearrangements(self):
        
        ''' Return the set of all scores related to this bipartition. '''
        
        if (self.reconfis == None): self._makeSPRRearrangements()
        return self.reconfis
    
    def getSPRScores(self,ls,node=None):
        
        ''' Given a landscape, return all possible scores, not actively performing
        scoring if not done. '''
        
        # Get starting information.
        scores = list() # Output scoreset.
        if not node:
            origin = self.topology # Starting topology.
            if not hasattr(origin,'orig'): ornewi = origin.toNewick()
            else: ornewi = origin.orig
            # Acquire node corresponding to this topology.
            start = ls.findTreeTopology(ornewi)
            if (start == None): return list() # Could not find.
        else: start = node 
            
        # Get neighbors.
        neighbors = ls.graph.neighbors(start)
        
        # Investigate all rearrangements.
        rearrangements = self.getSPRRearrangements()
        resultants = [x.toTree().struct for x in rearrangements]
        for neighbor in neighbors:
            node   = ls.getNode(neighbor)
            tree   = ls.getTree(neighbor)
            struct = tree.struct
            if struct in resultants:
                scores.append(tree.score[0])
        return scores
    
    def getMedianSPRScore(self,ls,node=None):
        
        ''' Given a landscape, return the median SPR score. '''
        
        li = [x for x in self.getSPRScores(ls,node) if x]
        if len(li) > 0: return median(li)
        else: return None
        
    def getBestSPRScore(self,ls,node=None):
        
        ''' Given a landscape, return the best SPR score. '''
        
        li = [x for x in self.getSPRScores(ls,node) if x]
        if len(li) > 0: return max(li)
        else: return None
