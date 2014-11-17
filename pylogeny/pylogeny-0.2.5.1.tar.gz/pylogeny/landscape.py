''' Encapsulate a phylogenetic tree space. A phylogenetic landscape or tree space refers to the entire combinatorial space comprising all possible phylogenetic tree topologies for a set of M{n} taxa. The landscape of M{n} taxa can be defined as consisting of a finite set M{T} of tree topologies. Tree topologies can be associated with a fitness function M{f(t_i)} describing their fit. This forms a discrete solution search space and finite graph M{(T, E) = G}. M{E(G)} refers to the neighborhood relation on M{T(G)}. Edges in this graph are bidirectional and represent transformation from one tree topology to another by a tree rearrangement operator. An edge between M{t_i} and M{t_j} would be notated as M{e_{ij}} in M{E(G)}. '''

# Date:   Jan 24 2014
# Author: Alex Safatli
# E-mail: safatli@cs.dal.ca

import networkx, tree
from random import choice
from scoring import getParsimonyFromProfiles as parsimony, getLogLikelihood as ll
from parsimony import profile_set as profiles
from networkx import components as comp, algorithms as alg
from tree import treeSet, numberRootedTrees, numberUnrootedTrees
from newick import parser, removeBranchLengths, postOrderTraversal
from rearrangement import TYPE_NNI, TYPE_SPR, TYPE_TBR

# Graph Object

class graph(object):
    
    ''' Define an empty graph object. '''
    
    def __init__(self,gr=None):
        if gr == None: self.graph = networkx.Graph()
        else: self.graph = gr
        self.defaultWeight = 0.
    
    def getNetworkXObject(self):
        
        ''' Return the internal networkx graph object. '''
        
        return self.graph    
    
    def __len__(self): return len(self.graph.node)

    def getSize(self):

        ''' Return the number of nodes in the graph. '''
        
        return len(self.graph.node)

    def getNodeNames(self):
        
        ''' Return the names/IDs of nodes in the graph. '''
        
        return self.graph.node.keys()
    
    def getNodes(self):      return self.graph.node.values()
    def getEdges(self):      return [self.getEdge(i,j) for i,j in self.graph.edges_iter()]
    def getEdgesFor(self,i): return [self.getEdge(i,j) for j in self.graph.neighbors(i)]
    def getNode(self,i):     return self.graph.node[i] 
    def getEdge(self,i,j):   return self.graph.get_edge_data(i,j)
    
    def __iter__(self):
        for node in self.graph.node.keys(): yield node
        
    def getNeighborsFor(self,i): return self.graph.neighbors(i)  
    
    def getDegreeFor(self,i):

        ''' Return in- and out-degree for node named i. '''
        
        return len(self.getNeighborsFor(i))
        
    def setDefaultWeight(self,w): self.defaultWeight = float(w)
    def clearEdgeWeights(self):
        for edge in self.getEdges():
            edge['weight'] = self.defaultWeight
        
    def getNumComponents(self):
        
        ''' Get the number of components of the graph. '''
        
        return comp.number_connected_components(self.graph)
    
    def getComponents(self):
        
        ''' Get the connected components in the graph. '''
        
        return comp.connected_components(self.graph)
        
    def getComponentOfNode(self,i):
        
        ''' Get the graph component of a given node. '''
        
        return comp.node_connected_component(self.graph,i)

    def getCliques(self):
        
        ''' Get the cliques present in the graph. '''
        
        return alg.clique.find_cliques(self.graph)
    
    def getCliqueNumber(self):

        ''' Get the clique number of the graph. '''
        
        return alg.clique.graph_clique_number(self.graph)
    
    def getNumCliques(self):
        
        ''' Get the number of cliques found in the graph. '''
        
        return alg.clique.number_of_cliques(self.graph)
    
    def getCliquesOfNode(self,i):
        
        ''' Get the clique that a node corresponds to. '''
        
        return alg.clique.cliques_containing_node(self.graph,i)
    
    def getCenter(self):
        
        ''' Get the centre of the graph. '''
        
        return alg.distance_measures.center(self.graph)
    
    def getDiameter(self):
        
        ''' Acquire the diameter of the graph. '''
        
        return alg.distance_measures.diameter(self.graph)    
    
    def getMST(self):

        ''' Acquire the minimum spanning tree for the graph. '''
        
        return alg.minimum_spanning_tree(self.graph)
    
    def hasPath(self,nodA,nodB):

        ''' See if a path exists between two nodes. '''
        
        return alg.has_path(self.graph,nodA,nodB)

    def getShortestPath(self,nodA,nodB):
        
        ''' Get the shortest path between two nodes. '''
        
        return alg.shortest_path(self.graph,nodA,nodB)

    def getShortestPathLength(self,nodA,nodB):
        
        ''' Get the shortest path length between two nodes. '''
        
        return alg.shortest_path_length(self.graph,nodA,nodB)

# Landscape: Subclass of Graph, TreeSet Objects

class landscape(graph,treeSet):
    
    ''' Defines an entire phylogenetic tree space. '''
    
    def __init__(self,ali,starting_tree=None,root=True,operator='SPR'):
        
        ''' Initialize the landscape. '''        
        
        super(landscape,self).__init__()
        
        # Fields
        self.alignment          = ali
        self.locks              = list()
        self.nextTree           = 0
        self.leaves             = None
        self.root               = None
        self.operator           = operator
        self.parsimony_profiles = None
        
        # Analyze alignment.
        if ali:
            # Get number of leaves.
            self.leaves = ali.getNumSeqs()
            # Get parsimony profile.
            self.parsimony_profiles = profiles(ali)           
                
        # Set up the root.
        if root:
            if not starting_tree:
                approx      = ali.getApproxMLTree()
                self.root   = self.addTree(approx)
            else: self.root = self.addTree(starting_tree)
            # Score this tree.
            node  = self.getNode(self.root)
            tre   = node['tree']
            topol = tre.toTopology()
            new   = topol.toNewick()
            if not (tre.score):
                sc = parsimony(new,p)
                tre.score = (None,sc)            
        
    def getAlignment(self): 
        
        ''' Acquire the alignment object associated with this space. '''
        
        return self.alignment
    
    def getNumberTaxa(self):
        
        ''' Return the number of different taxa present in any respective tree
        in the landscape. '''
        
        return self.leaves

    def getPossibleNumberRootedTrees(self):
        
        ''' Assuming all of the trees in the space are rooted, return the 
        maximum possible number of unrooted trees that can possibly be generated
        for the number of taxa of trees in the landscape. '''
        
        return numberRootedTrees(self.leaves)
    
    def getPossibleNumberUnrootedTrees(self):
        
        ''' Assuming all of the trees in the space are unrooted, return the 
        maximum possible number of unrooted trees that can possibly be generated
        for the number of taxa of trees in the landscape. '''
        
        return numberUnrootedTrees(self.leaves)
    
    def getRootTree(self):
        
        ''' Acquire the first tree that was placed in this space. '''
        
        return self.root
    
    def setAlignment(self,ali):
        
        ''' Set the alignment present in this landscape. WARNING; will not
        modify existing scores. '''
        
        self.alignment          = ali
        self.leaves             = ali.getNumSeqs()
        self.parsimony_profiles = profiles(ali)
    
    # Node Management
                
    def _newNode(self,i,tobj):
        
        ''' PRIVATE: Add a new node. '''
        
        node = self.graph.node[i]
        node['explored'] = False
        node['tree']     = tobj
        node['failed']   = False
        if tobj.score == None:
            # Get the parsimony since this is fast; set likelihood
            # to nothing.
            if self.alignment:
                tobj.score = (None,parsimony(
                    tobj.newick,self.parsimony_profiles))
            else: tobj.score = (None,None)
        elif tobj.score[1] == None:
            # Get the parsimony since this is fast; set likelihood
            # to nothing.
            if self.alignment:
                tobj.score = (tobj.score[0],parsimony(
                    tobj.newick,self.parsimony_profiles))            

    def getTree(self,i):
        
        ''' Get the tree object for a tree by its ID or name i. '''
        
        if not i in self.graph.node: return None
        return self.getNode(i)['tree']

    def getVertex(self,i):
        
        ''' Acquire a vertex object from the landscape; this is a 
        high-level representation of a tree in the landscape with
        additional functionality. Object created upon invocation of
        this function. '''
        
        return vertex(i,self.getNode(i),self)

    def removeTree(self,tree):
        
        ''' Remove a tree by object. '''
        
        for t in self.graph.node:
            if self.getTree(t) == tree:
                self.graph.remove_node(t)
                return True
        return False
        
    def addTree(self,tree):
        
        ''' Add a tree to the landscape. '''
        
        if not hasattr(self,'nextTree'):
            # Set up next tree iterable.
            self.nextTree = max(self.graph.node.keys())+1
        
        # Add tree with unique ID if not present.
        if tree.getName() is '':
            t = self.nextTree
            tree.name = t
        self.graph.add_node(tree.getName())
        self._newNode(tree.getName(),tree)
        self.nextTree += 1
        return tree.getName()

    def exploreRandomTree(self,i,type=TYPE_SPR):
        
        ''' Acquire a single neighbor to a tree in the landscape by performing
        a random rearrangement of type SPR (by default), NNI, or TBR. Rearrangement
        type is provided as a rearrangement module type definition of form, for example,
        TYPE_SPR, TYPE_NNI, etc. '''
        
        # Get parsimony profiles.
        p = self.parsimony_profiles
        
        # Check node.
        node  = self.getNode(i)
        if (node['explored']): return None
        tre   = node['tree']
        topol = tre.toTopology()
        new   = topol.toNewick()
        isvi  = self._isViolating(topol)
        
        # Check for locks.
        if hasattr(self,'locks'):
            for lock in self.locks:
                hasthis = topol.getBranchFromBipartition(lock)
                if (hasthis): topol.lockBranch(hasthis)
        
        # Perform an exploration not yet done.
        branches = topol.getBranches()
        while (len(branches) > 0):
            
            bra  = choice(branches)
            branches.remove(bra)
            enum = topol.iterTypeForBranch(bra,type)
        
            for en in enum:
                
                # Get metadata.
                typ = en.getType()
                t   = en.toTree()
                new = t.getNewick()
                stt = t.getStructure()
    
                # See if already been found.
                inlandscape = self.findTreeTopologyByStructure(stt)
                if (inlandscape):
                    # Is in landscape; has connection to tree?
                    if not (inlandscape == i): 
                        if not self.graph.has_edge(inlandscape,i):
                            self.graph.add_edge(inlandscape,i)
                            self.getEdge(inlandscape,i)['weight'] = self.defaultWeight
                    continue
    
                # See if tree violating existing locks.
                if isvi:
                    en = en.toTopology()
                    if self._isViolating(en): continue
    
                # Score.
                scr = parsimony(new,p)
                t.score  = (None,scr)
                t.origin = typ
                
                # Add to landscape.
                j = self.addTree(t)
                self.graph.add_edge(i,j)
                self.getEdge(i,j)['weight'] = self.defaultWeight
                return j
        
        # Set explored to True.
        node['explored'] = True 
        
        return None        

    def exploreTree(self,i,type=TYPE_SPR):
        
        ''' Get all neighbors to a tree named i in the landscape using a respective
        rearrangement operator as defined in the rearrangement module. Rearrangement
        type is provided as a rearrangement module type definition of form, for example,
        TYPE_SPR, TYPE_NNI, etc. By default, this is TYPE_SPR. '''
        
        # Get parsimony profiles.
        p = self.parsimony_profiles
        
        # Check node.
        node  = self.getNode(i)
        if (node['explored']): return False
        tre   = node['tree']
        topol = tre.toTopology()
        new   = topol.toNewick()
        isvi  = self._isViolating(topol)
        
        # Check for locks.
        if hasattr(self,'locks'):
            for lock in self.locks:
                hasthis = topol.getBranchFromBipartition(lock)
                if (hasthis): topol.lockBranch(hasthis)
        
        # Perform full-enumeration exploration (1 move).
        enum = topol.allType(type)
        
        for en in enum:
            
            # Get metadata.
            typ = en.getType()
            t   = en.toTree()
            new = t.getNewick()
            stt = t.getStructure()

            # See if already been found.
            inlandscape = self.findTreeTopologyByStructure(stt)
            if (inlandscape):
                # Is in landscape; has connection to tree?
                if not (inlandscape == i): 
                    if not self.graph.has_edge(inlandscape,i):
                        self.graph.add_edge(inlandscape,i)
                        self.getEdge(inlandscape,i)['weight'] = self.defaultWeight
                continue

            # See if tree violating existing locks.
            if isvi:
                en = en.toTopology()
                if self._isViolating(en): continue

            # Score.
            scr = parsimony(new,p)
            t.score  = (None,scr)
            t.origin = typ
            
            # Add to landscape.
            j = self.addTree(t)
            self.graph.add_edge(i,j)
            self.getEdge(i,j)['weight'] = self.defaultWeight
        
        # Set explored to True.
        node['explored'] = True 
        
        return True

    # Lock Management
        
    def getLocks(self): return self.locks 
    
    def toggleLock(self,lock):
        
        ''' Add a biparition to the list of locked bipartitions if not 
        present; otherwise, remove it. Return status of lock. '''
        
        toggle = False
        if lock in self.getLocks(): self.locks.remove(lock)
        else:
            self.locks.append(lock)
            toggle = True
        return toggle
    
    def lockBranchFoundInTree(self,tr,br):
        
        ''' Given a tree node and a branch object, add a given 
        bipartition to the bipartition lock list. Returns true if locked. '''

        # Check for presence of tree.
        g = self.graph.node
        if (not tr in g): return None
        
        # Acquire metadata for tree.
        tr = self.getTree(tr)
        topl = tr.toTopology()
        
        # Get bipartition for branch.
        bipa  = tree.bipartition(topl,br)
        
        # Toggle the lock.
        self.toggleLock(bipa)
        return bipa
    
    def getBipartitionFoundInTreeByIndex(self,tr,brind,topol=None):
        
        ''' Given a tree node and a branch index, return the associated
        bipartition. '''
        
        # Check for presence of tree.
        if (not topol) and (not tr in self.graph.node): return None
        
        # Acquire metadata for tree.
        if not topol:
            tr = self.graph.node[tr]['tree']
            topl = tr.toTopology()
        
        # Get bipartition for branch.
        nodes = postOrderTraversal(topl.getRoot())
        if not brind in xrange(len(nodes)): return None
        bnode = nodes[brind]
        bipa  = tree.bipartition(topl,bnode.parent)
        
        # Return the bipartition.
        return bipa
            
    def lockBranchFoundInTreeByIndex(self,tr,brind):
        
        ''' Given a tree node and a branch index, add a given 
        bipartition to the bipartition lock list. Returns true if locked. '''

        # Check for presence of tree.
        if (not tr in self.graph.node): return None
        
        # Acquire metadata for tree.
        tree = self.graph.node[tr]['tree']
        topl = tree.toTopology()
        
        # Get bipartition for branch.
        bipa = self.getBipartitionFoundInTreeByIndex(tr,brind,topl)
        
        # Toggle the lock.
        self.toggleLock(bipa)
        return bipa

    def _isViolating(self,topo):
        
        ''' PRIVATE: Given a topology, determine if it is
        violating existing locks. '''
        
        if len(self.locks) > 0:
            for lock in self.locks:
                hasit = topo.getBranchFromBipartition(lock)
                if (not hasit): return True
        return False
    
    def isViolating(self,i):
        
        ''' Determine if a tree is violating any locks intrinsic 
        to the landscape. '''
    
        if i in self.graph.node.keys():
            node = self.getNode(i)
            topo = node['tree'].toTopology()
            return self._isViolating(topo)
        return False

    # Search Methods

    def __getitem__(self, i): return self.graph.node[i]

    def indexOf(self, tr):
        
        ''' Acquire the index/name in this landscape of a tree object. Returns -1
        if not found. '''
        
        for t in self.graph.node:
            if self.getTree(t) == tr: return t
        return -1

    def findTree(self,newick):
        
        ''' Find a tree by Newick string, taking into account branch lengths. Returns
        the name of this tree in the landscape. '''
        
        for t in self.graph.node:
            if self.getTree(t).newick == newick: return t
        return None
    
    def findTreeTopology(self,newick):
        
        ''' Find a tree by topology, not taking into account branch lengths. '''
        
        s = parser(newick).parse()
        removeBranchLengths(s)
        s = str(s) + ';'
        return self.findTreeTopologyByStructure(s)
    
    def findTreeTopologyByStructure(self,struct):
        
        ''' Find a tree by topology, not taking into account branch lengths,
        given the topology. '''
        
        for t in self.graph.node:
            if self.getTree(t).getStructure() == struct: return t
        return None
        
    def getBestImprovement(self,i):
        
        ''' For a tree in the landscape, investigate neighbors to find 
        a tree that leads to the best improvement of fitness function score
        on the basis of likelihood. '''
        
        nodes = self.graph.node
        tree  = self.getTree
        ml    = lambda d: tree(d).score[0]
        if (not i in nodes):
            raise LookupError('No tree by that name in landscape.' % (i))
        node  = nodes[i]
        near  = self.graph.neighbors(i)
        if (len(near) == 0): return None
        best  = max(near,key=ml)
        if (best != None and ml(best) > ml(i)): return best
        else: return None
        
    def getPathOfBestImprovement(self,i):
        
        ''' For a tree in the landscape, investigate neighbors iteratively
        until a best path of score improvement is found on basis of likelihood. '''
        
        path  = []
        nodes = self.graph.node
        if (not i in nodes):
            raise LookupError('No tree by that name in landscape.' % (i))
        node = nodes[i]
        curs = node
        impr = self.getBestImprovement(i)
        if not impr: return list()
        else: besc = self.getTree(impr).score[0]
        
        while (besc != None and besc > curs['tree'].score[0]):
            path.append(impr)
            curs = nodes[impr]
            impr = self.getBestImprovement(i)
            if not impr: besc = None
            else:        besc = self.getTree(impr).score[0]
        
        return path
    
    def getAllPathsOfBestImprovement(self):
        
        ''' Return all paths of best improvement as a dictionary. '''
        
        paths = {}
        for node in self.graph.node:
            paths[node] = self.getPathOfBestImprovement(node)
        return paths    
    
    def iterAllPathsOfBestImprovement(self):
        
        ''' Return an iterator for all paths of best improvement. '''
        
        for node in self.graph.node:
            yield self.getPathOfBestImprovement(node)
    
    def isLocalOptimum(self,i):
        
        ''' Determine if a tree is, without any doubt, a local optimum. '''
        
        nodes = self.graph.node
        if (self.getTree(i).score[0] == None):
            return False
        elif (not self.getNode(i)['explored']):
            return False
        p = self.getPathOfBestImprovement(i)
        if (len(p) == 0):
            near = self.graph.neighbors(i)
            if (len(near) == 0): return False
            for node in [nodes[x] for x in near]:
                if node['tree'].score[0] == None and \
                   'failed' in node and not node['failed']:
                    return False
            return True
        return False
    
    def getLocalOptima(self):
        
        ''' Get all trees in the landscape that can be labelled as a local
        optimum. '''
        
        opt = []
        for node in self.graph.node:
            if (self.isLocalOptimum(node)): opt.append(node)
        return opt
    
    def getGlobalOptimum(self):
        
        ''' Get the global optimum of the current space. '''
        
        optima = self.getLocalOptima()
        gmax   = max(
            optima,key=lambda d: self.getTree(d).score[0])
        return gmax

    # Output Methods
    
    def __str__(self): return self._dump()
    
    def _dump(self,proper=True):
        
        trees = []
        for t in self.getNodeNames():
            trees.append(self.getVertex(t))
        return '\n'.join([t.getProperNewick() for t in trees])

    def toTreeSet(self):
        
        ''' Convert this landscape into an unorganized set of trees 
        where taxa names are transformed to their original form (
        i.e. not transformed to a state friendly for the Phylip format). '''
        
        treeset = treeSet()
        for t in self.getNodeNames():
            treeset.addTree(tree(self.getVertex(t).getProperNewick()))
        return treeset

# Comprising Vertices of Landscapes

class vertex(object):
    
    ''' Encapsulate a single vertex in the landscape and add convenient
    functionality to alias parent landscape functions. '''
    
    def __init__(self,i,obj,ls):
        self.id  = i
        self.obj = obj
        self.ls = ls
        self.ali = ls.alignment
    
    def getIndex(self):       return self.id
    def getDict(self):        return self.obj
    def getObject(self):      return self.getDict()
    def getTree(self):        return self.obj['tree']
    def getNewick(self):      return self.getTree().getNewick()
    def getScore(self):       return self.getTree().score
    def getOrigin(self):      return self.getTree().origin
    def getNeighbors(self):   return self.ls.graph.neighbors(self.id)
    def getDegree(self):      return len(self.getNeighbors())
    def isLocalOptimum(self): return self.ls.isLocalOptimum(self.id)
    def isExplored(self):     return self.obj['explored']
    def isFailed(self):       return ('failed' in self.obj and self.obj['failed'])
    
    def approximatePossibleNumNeighbors(self):
        
        ''' Approximate the possible number of neighbors to this vertex
        by considering the type of tree rearrangement operator. '''

        n = self.ls.getNumberTaxa()
        if self.ls.operator == 'SPR': return 4*(n-3)*(n-2)
        raise AssertionError('Landscape rearrangement operator not defined!')
    
    def scoreLikelihood(self):
        
        if self.getScore()[0] == None:
            l = ll(self.getTree(),self.ali)
            self.obj['tree'].score = (l,self.getScore()[1])
            return l
        else: return self.getScore()[0]
    
    def getBestImprovement(self):
        
        ''' Alias function for function of same name in parent
        landscape. '''
        
        return self.ls.getBestImprovement(self.id)
    
    def getPathOfBestImprovement(self):    
    
        ''' Alias function for function of same name in parent
        landscape. '''
        
        return self.ls.getPathOfBestImprovement(self.id)
    
    def isBestImprovement(self):
        
        ''' Check to see if this vertex is a best move for another node. '''
        
        for neighbor in self.getNeighbors():
            if self.ls.getTree(neighbor).score[0] < self.getTree().score[0]:
                if self.ls.getBestImprovement(neighbor) == self.id:
                    return True
        return False
    
    def isViolating(self):
        
        ''' Alias function for function of same name in parent
        landscape. '''
        
        return self.ls.isViolating(self.id)

    def getProperNewick(self):
        
        ''' Get the proper Newick string for a tree. '''
        
        if self.ali == None: return self.getNewick()
        return self.ali.reinterpretNewick(self.getNewick())
    
    def getBipartitions(self):
    
        ''' Get all bipartitions for this vertex. '''
        
        # Get tree object.
        tr = self.getTree()
        
        # Get corresponding topology.
        topo  = tr.toTopology()
        nodes = postOrderTraversal(topo.getRoot())
        
        # Get branches + bipartitions of the topology.
        bp = []
        br = [x.parent for x in nodes]
        for b in br:
            if b:
                bi = tree.bipartition(topo,b)
                bp.append(bi)
            else: bp.append(None)
        
        # Return the bipartitions.
        return bp
    
    def getBipartitionScores(self):
        
        ''' Get all corresponding bipartition vectors of SPR scores. '''
        
        return [x.getSPRScores() for x in self.getBipartitions()]
    
    def getNeighborsOfBipartition(self,bi):
        
        ''' Get corresponding neighbors of a bipartition in this vertex's tree. '''
        
        l     = self.ls
        re    = bi.getSPRRearrangements()
        lsids = [l.findTreeTopology(x.toTree().getStructure()) for x in re]
        return lsids
    
    def getNeighborsOfBranch(self,br):
        
        ''' Get corresponding neighbors of a branch in this vertex's tree. '''
        
        tr   = self.getTree()
        topl = tr.toTopology()
        bipa = tree.bipartition(topl,br)
        return self.getNeighborsOfBipartition(bipa)

    
