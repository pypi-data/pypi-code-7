# -*- python -*-
#
#  This file is part of the cinapps.tcell package
#
#  Copyright (c) 2012-2013 - EMBL-EBI
#
#  File author(s): Thomas Cokelaer (cokelaer@ebi.ac.uk)
#
#  Distributed under the GLPv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: www.cellnopt.org
#
##############################################################################
""".. topic:: **One of the main data structures of cellnopt to manipulate networks**"""
from __future__ import print_function
import os
import copy
import tempfile
import itertools
import subprocess
import shutil
import json

import matplotlib
import pylab
import networkx as nx
import numpy as np
from easydev import Logging

# cellnopt modules
from cno.io.sif import SIF
from cno.io.midas import XMIDAS
from cno.io.reactions import Reaction
from cno.misc import CNOError
from cno.core import DevTools
import colormap

__all__ = ["CNOGraph", "CNOGraphAttributes"]


class Link(object):
    """Simple class to handle links
   
    This class is used internally to simplify code.

    .. doctest::

        >>> from cno.io.cnograph import Link
        >>> l = Link("+")
        >>> l.name
        "activation"
        >>> l.link
        "+"

    """
    def __init__(self, link):
        self._link = None
        self.link = link

    def _set_link(self, link):
        if link == "+":
            self.name = 'activation'
        elif link == '-':
            self.name = 'inhibition'
        else:
            raise ValueError("Only + and - link are valid")
        self._link = link
    def _get_link(self):
        return self._link
    link = property(_get_link, _set_link, doc="Getter/Setter for links")


class Attributes(dict):
    """Simple dictionary to handle attributes (nodes or eges)"""
    def __init__(self, color, **kargs):
        self['color'] = color
        for k,v in kargs.iteritems():
            self[k] = v

class EdgeAttributes(Attributes):
    """Simple dictionary to handle edge attributes"""
    def __init__(self, penwidth=1, color="black", arrowhead="normal", **kargs):
        super(EdgeAttributes, self).__init__(color=color, **kargs)
        self['penwidth'] = penwidth
        self['arrowhead'] = arrowhead

class NodeAttributes(dict):
    """Simple dictionary to handle node attributes
    
    Used by the :class:`CNOGraph`.

    ::

        >>> a = Attributes(color="red", fillcolor="white")
        >>> assert a['color'] == "red"
        True

    """
    def __init__(self, color="black", fillcolor="white", shape="rectangle",
                 style="filled,bold", **kargs):
        """

        :param color: color of the border
        :param fillcolor: color inside the shape
        :param shape color inside the shape
        :param style: color inside the shape
        """
        super(NodeAttributes, self).__init__(color=color, **kargs)

        #self['color'] = color
        self['fillcolor'] = fillcolor
        self['shape'] = shape
        self['style'] = style


class CNOGraphAttributes(object):
    """

    define attributes of the cnograp when calling the plotting function.
    """
    def __init__(self):

        self.attributes = {
               'activation': EdgeAttributes(color='black', arrowhead="normal"),
               'inhibition': EdgeAttributes(color='red', arrowhead="tee"),
               'stimuli': NodeAttributes(fillcolor='#9ACD32'),
               'inhibitors': NodeAttributes(fillcolor='orangered'),
               'signals': NodeAttributes(fillcolor='lightblue'),
               'nonc': NodeAttributes( fillcolor='gray', style='diagonals, filled'),
               'compressed': NodeAttributes(fillcolor="white",style='dashed', penwidth=2),
               'others': NodeAttributes(fillcolor="white",style='filled,bold',penwidth=2),
               'and': NodeAttributes(shape='circle',style='filled',width=.1,
                            height=.1, fixedsize=True, label='')
               }
    def keys(self):
        return self.attributes.keys()
    def __getitem__(self, key):
        return self.attributes[key]


class CNOGraph(nx.DiGraph):
    """Data structure (Digraph) used to manipulate networks

    The networks can represent for instance a protein interaction network (PIN).

    CNOGraph is a data structure dedicated to the analysis of
    phosphorylation data within protein-protein interaction networks
    but can be used in a more general context. Note that CNOGraph inherits 
    from the **directed graph** data structure of networkx.

    However, we impose links between nodes to be restricted to two types:
        * "+" for activation
        * "-" for inhibition.

    An empty instance can be created as follows::

        c = CNOGraph()

    and edge can be added as follows::

        c.add_edge("A", "B", link="+")
        c.add_edge("A", "C", link="-")

    An even simpler way is to add :class:`cno.io.reactions.Reaction`, which can be strings
    or instance of the Reaction class.

    The methods :meth:`add_node`  and :meth:`add_edge` methods can be used to
    populate the graph. However, it is also possible to read a network
    stored in a file in :class:`cno.io.sif.SIF` format::

        >>> from cno import CNOGraph, cnodata
        >>> pknmodel = cnodata("PKN-ToyPB.sif")
        >>> c = CNOGraph(pknmodel)

    The SIF model can be a filename, or an instance of
    :class:`~cno.io.sif.SIF`. Note for CellNOpt users
    that if **and** nodes are contained in the original SIF files, they are
    transformed int AND gates using "^" as the logical AND.

    Other imports are available, in particular :meth:`read_sbmlqual`.
    
    You can add or remove nodes/edges in the CNOGraph afterwards using NetworkX methods.

    When instanciating a CNOGraph instance, you can also populate data from 
    a :class:`~cno.io.midas.XMIDAS` data instance or a MIDAS filename. 
    MIDAS file contains measurements made on proteins
    in various experimental conditions (stimuli and inhibitors). The names of
    the simuli, inhibitors and signals are used to color the nodes in the
    plotting function. However, the data itself is not used.

    If you don't use any MIDAS file as input, you can set the
    stimuli/inhibitors/signals manually by filling the hidden attributes
    _stimuli, _signals and _inhibitors with list of nodes contained in the graph.

    .. rubric:: Node and Edge attributes

    The node and edge attributes can be accessed as follows (and changed)::

        >>> c.node['egf']
        {'color': u'black',
         u'fillcolor': u'white',
         'penwidth': 2,
         u'shape': u'rectangle',
         u'style': u'filled,bold'}

        >>> c.edge['egf']['egfr']
        {u'arrowhead': u'normal',
         u'color': u'black',
         u'compressed': [],
         'link': u'+',
         u'penwidth': 1}

    .. rubric:: OPERATORS

    CNOGraph is a data structure with useful operators (e.g. union). Note,
    however, that these operators are applied on the topology only (MIDAS
    information is ignored). For instance, you can add graphs with the **+** operator
    or check that there are identical ::

        c1 = CNOGraph()
        c1.add_reaction("A=B")
        c2 = CNOGraph()
        c2.add_reaction("A=C")
        c3 = c1 +c2

    Let us illustrate the + operation with another example. Let us consider the following graphs:

    .. plot::
        :include-source:
        :width: 30%

        from cno import CNOGraph
        c1 = CNOGraph()
        c1.add_edge("A","B", link="+")
        c1.add_edge("A","C", link="-")
        c1.plot()


    .. plot::
        :include-source:
        :width: 30%

        from cno import CNOGraph
        c2 = CNOGraph()
        c2.add_edge("A","E", link="+")
        c2.add_edge("C","E", link="+")
        c2.plot()

    ::

        (c1+c2).plot()


    .. plot::
        :width: 50%

        from cno import CNOGraph
        c1 = CNOGraph()
        c1.add_edge("A","B", link="+")
        c1.add_edge("A","C", link="-")
        c1.plot()
        c2 = CNOGraph()
        c2.add_edge("A","E", link="+")
        c2.add_edge("C","E", link="+")
        c2.plot()
        (c1+c2).plot()

    You can also substract a graph from another one::

        c3 = c1 - c2
        c3.nodes()

    The new graph should contains only one node (B). Additional functionalities
    such as :meth:`intersect`, :meth:`union` and :meth:`difference` can be used to see the difference
    between two graphs.

    .. rubric:: PLOTTING

    There are plotting functionalities to look at the graph, which are based on graphviz
    library. For instance, the :meth:`plot` function is quite flexible. If a MIDAS file
    is provided, the default behaviour follow CellNOptR convention,  where stimuli are 
    colored in green, inhibitors in red and measurements in blue:

    .. plot::
        :include-source:
        :width: 50%

        from cno import CNOGraph, cnodata
        pknmodel = cnodata("PKN-ToyPB.sif")
        data = cnodata("MD-ToyPB.csv")
        c = CNOGraph(pknmodel, data)
        c.plot()

    If you did not use any MIDAS file as input parameter, you can still populate the hidden fields
    :attr:`_stimuli`, :attr:`_inhibitors`, :attr:`_signals`.

    You can also overwrite this behaviour by using the node_attribute parameter when
    calling :meth:`plot`. For instance, if you call :meth:`centrality_degree`, which
    computes and populate the node attribute
    **degree**. You can then call plot as follows to replace the default
    color:

    .. plot::
        :include-source:
        :width: 50%

        from cno import CNOGraph, cnodata
        pknmodel = cnodata("PKN-ToyPB.sif")
        data = cnodata("MD-ToyPB.csv")
        c = CNOGraph(pknmodel, data)
        c.centrality_degree()
        c.plot(node_attribute="centrality_degree", colorbar)

    Similarly, you can tune the color of the edge attribute. See the :meth:`plot` for more details.

    .. seealso::  tutorial, user guide

    .. seealso:: The :class:`cno.io.xcnograph.XCNOGraph` provides many more tools for plotting
        various information on the graph structure.


    """
    def __init__(self, model=None, data=None, verbose=False, **kargs):
        """.. rubric:: Constructor

        :param str model: optional network in SIF format. Can be the filename
            or instance of :class:`~cno.io.sif.SIF`
        :param data: optional data file in MIDAS format. Can be a filename or
            instance of :class:`~cno.io.midas.XMIDAS`
        :param bool verbose:
        :param str celltype: if a MIDAS file contains more that 1 celltype, you
            must provide a celltype name


        """
        super(CNOGraph, self).__init__(**kargs)
        self.kargs = kargs.copy()

        # This is a DIgraph attribute
        # self.graph is a DiGraph attribute that is overwritten sometinmes

        self.graph_options = {
           'graph': {
                "title": "CNOGraph output generated by cno",
                "dpi":200,
                'rankdir':'TB', # TB, LR, RL
                'ordering': "out",
                'splines':True,
                'fontsize': 22,
                 #'nodesep': .5,
                 #'ranksep':.6,
                'ratio':'auto', # numeric,  'fill','compress','expand','auto'
                # 0.8 is good for laptop screens. 2 is good for 
                'size': "10,10",
                # 'fontname': 'helvetica',
                },
            'node':{
                #'width':1,
                #'fontsize':40,
                #'height':1,
                #'width':2,
                'fontname':'bold'
                 },
            'edge': {
                'minlen':1,
                'color':'black'
                }
            } 

        # cellnoptR has always the same layout:
        #s.model.graph_options['graph']['nodesep'] = 0.5
        #s.model.plot(rank_method='same')


        self.plot_options = {
                'colorbar.orientation': 'horizontal',
                'colorbar.shrink': 0.5,
                'colorbar.fraction': 0.15,
                'colorbar.pad': 0.1,
                }

        #: nodes and edges attributes. See :class:`CNOGraphAttributes`
        self.attributes = CNOGraphAttributes()

        self.and_symbol = "^"
        self.or_symbol = "+"

        self._midas = None
        self._verbose = verbose
        self.logging = Logging(self.verbose)

        self._compress_ands = False
        #: stimuli
        self._stimuli = []
        #: inhibitors
        self._inhibitors = []

        self._compressed = []
        self._signals =[]
        self._nonc = None

        # the model
        if hasattr(model, '__class__') and \
            model.__class__.__name__ in ['CNOGraph', 'XCNOGraph']:
            for node in model.nodes():
                self.add_node(unicode(node))
            for edge in model.edges(data=True):
                if "link" in edge[2]:
                    self.add_edge(unicode(edge[0]), unicode(edge[1]), link=edge[2]['link'])
                else:
                    self.add_edge(unicode(edge[0]), unicode(edge[1]), link="+")
            self.set_default_node_attributes() # must be call if sif or midas modified.
            self.filename = None
            if model.midas is not None:
                self.midas = model.midas.copy()
        elif model is None:
            self.filename = None

        elif isinstance(model, str):
            if model.endswith('.sif'):
                self.read_sif(model)
                self.filename = model[:]
            elif model.endswith(".xml"):
                self.read_sbmlqual(model)
                self.filename = model[:]
            else:
                raise CNOError("Only filenames with .sif and .xml (SBML-qual) extension are recognised.")
        elif isinstance(model, SIF):
            self.read_sif(model)
            self.filename = 'undefined'

        # the data
        if self.midas is None:
            self.midas = data

        self._colormap = colormap.Colormap()

    def _set_verbose(self, verbose):
        self.logging.debugLevel = verbose
        self.midas.logging.debugLevel = verbose
    def _get_verbose(self):
        return self._verbose
    verbose = property(_get_verbose, _set_verbose)

    # SOME PROPERTIES
    def _get_midas(self):
        return self._midas
    def _set_midas(self, data):
        if isinstance(data, str):
            self._midas = XMIDAS(data, cellLine=self.kargs.get("cellLine", None),
                                 verbose=self.verbose)
        elif isinstance(data, XMIDAS):
            self._midas = copy.deepcopy(data)
        elif data == None:
            self._midas = data
        else:
            msg = "Incorrect data, Must a valid MIDAS file or instance of XMIDAS class {}"
            raise ValueError(msg.format(data))
        self.check_data_compatibility()
        self.set_default_node_attributes()
    midas = property(fget=_get_midas, fset=_set_midas,
                     doc="MIDAS Read/Write attribute.")

    def _get_stimuli(self):
        stimuli = list(self._stimuli[:])
        if self.midas:
            stimuli += self.midas.names_stimuli[:]
        return stimuli
    stimuli = property(_get_stimuli,
            doc="list of stimuli found in the :attr:`midas` and hidden attribute :meth:`_stimuli`")

    def _get_inhibitors(self):
        inhibitors = list(self._inhibitors)
        if self.midas:
            inhibitors += self.midas.names_inhibitors[:]
        return inhibitors
    inhibitors = property(_get_inhibitors,
            doc="list of inhibitors found in the :attr:`midas` and hidden attribute :attr:`_inhibitors`")

    def _get_signals(self):
        signals = list(self._signals) # do not reference
        if self.midas:
            signals += list(self.midas.names_signals)
        return signals
    signals = property(_get_signals,
            doc="list of signals found in the :attr:`midas` and hidden attribute :meth:`_signals`")

    # METHODS
    def read_sif(self, model):
        """If the SIF file changes, we need to rebuild the graph."""
        # takes the SIF input file and build up the CNOGraph. remove all nodes
        # before
        self.clear()
        self.logging.debug("reading the model")

        if isinstance(model, (str, unicode)):
            sif = SIF(model)
        elif isinstance(model, SIF):
            sif = model
        else:
            raise ValueError("The sif input must be a filename to a SIF file or an instance of the SIF class")

        # add all reactions
        self.add_reactions(sif.reactions)

        # now, we need to set the attributes, only if we have a cnolist,
        # otherwise color is the default (white)
        self.set_default_node_attributes() # must be call if sif or midas modified.
        self.logging.debug("model loaded")

    def _add_simple_reaction(self, reac):
        """A=B or !A=B"""

        #reac = Reaction(reac) # validate the reaction
        #reac = reac.name
        lhs, rhs = reac.split("=", 1)
        #if reac == "":
        #    self.add_node(rhs)
        if rhs == "":
            self.add_node(lhs)
        else:
            if lhs.startswith("!"):
                link = "-"
                lhs = lhs[1:]
            else:
                link = "+"
            if self.has_edge(lhs, rhs):
                if self[lhs][rhs]['link'] == link:
                    self.logging.info("skip existing reactions %s %s %s" % (lhs, link, rhs))
                else:
                    self.add_edge(lhs, rhs, link=link)
            else:
                self.add_edge(lhs,rhs, link=link)

    def add_reactions(self, reactions):
        for reac in reactions:
            self.add_reaction(reac)

    def add_reaction(self, reac):
        """Add nodes and edges given a reaction

        :param str reac: a valid reaction. See below for examples

        Here are some valid reactions that includes NOT, AND and OR gates. + is an OR
        and ^ character is an AND gate::

            >>> s.add_reaction("A=B")
            >>> s.add_reaction("A+B=C")
            >>> s.add_reaction("A^C=E")
            >>> s.add_reaction("!F+G=H")

        .. plot::
            :width: 50%
            :include-source:

            from cno import CNOGraph
            c = CNOGraph()
            c.add_reaction("a+b^c+e+d^h=Z")
            c.plot()


        """
        reac = Reaction(reac)
        lhs, rhs = reac.lhs, reac.rhs

        # if there is an OR gate, easy, just need to add simple reactions
        # A+!B=C is splitted into A=C and !B=C

        for this_lhs in lhs.split("+"):
            # + has priority upon ^ unlike in maths so we can split with +
            # A+B^C^D+E=C means 3 reactions: A=C, E=C and B^C^D=C
            if self.isand(this_lhs) is False:
                self._add_simple_reaction(this_lhs + "=" + rhs)
            else:
                and_gate_name = this_lhs + "=" + rhs
                # and gates need a little bit more work
                self.add_edge(and_gate_name, rhs, link="+") # the AND gate and its the unique output
                # now the inputs
                for this in this_lhs.split(self.and_symbol):
                    self._add_simple_reaction(this + "=" + and_gate_name)


    def set_default_edge_attributes(self,  **attr):
        if "compressed" not in attr.keys():
            attr["compressed"] = []

        link = Link(attr.get("link"))
        attrs = self.attributes[link.name]
        for k in attrs.keys():
            attr[k] = attrs[k]
        return attr

    def reset_edge_attributes(self):
        """set all edge attributes to default attributes

        .. seealso:: :meth:`set_default_edge_attribute`

        if we set an edge label, which is an AND ^, then plot fails in this function
        c.edge["alpha^NaCl=HOG1"]['label'] = "?"
        """
        for edge in self.edges():
            attrs = self.edge[edge[0]][edge[1]]
            attrs = self.set_default_edge_attributes(**attrs)
            self.edge[edge[0]][edge[1]] = attrs

    def add_edge(self, u, v, attr_dict=None, **attr):
        """adds an edge between node u and v.

        :param str u: source node
        :param str v: target node
        :param str link: compulsary keyword. must be "+" or "-"
        :param dict attr_dict: dictionary, optional (default= no attributes)
             Dictionary of edge attributes.  Key/value pairs will update existing
             data associated with the edge.
        :param attr: keyword arguments, optional
            edge data (or labels or objects) can be assigned using keyword arguments.
            keywords provided will overwrite keys provided in the **attr_dict** parameter

        .. warning:: color, penwidth, arrowhead keywords are populated according to the
            value of the link.

        * If link="+", then edge is black and arrowhead is normal.
        * If link="-", then edge is red and arrowhead is a tee

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            c = CNOGraph()
            c.add_edge("A","B",link="+")
            c.add_edge("A","C",link="-")
            c.add_edge("C","D",link="+", mycolor="blue")
            c.add_edge("C","E",link="+", data=[1,2,3])

        If you want multiple edges, use add_reaction() method.

            c.add_reaction("A+B+C=D")

        equivalent to ::

            c.add_edge("A", "D", link="+")
            c.add_edge("B", "D", link="+")
            c.add_edge("C", "D", link="+")


        Attributes on the edges can be provided using the parameters **attr_dict** (a dictionary)
        and/or ****attr**, which is a list of key/value pairs. The latter will overwrite the
        key/value pairs contained in the dictionary. Consider this example::

            c = CNOGraph()
            c.add_edge("a", "c", attr_dict={"k":1, "data":[0,1,2]}, link="+", k=3)
            c.edges(data=True)
            [('a',
            'c',
                {'arrowhead': 'normal',
                'color': 'black',
                'compressed': [],
                'k':3
                'link': '+',
                'penwidth': 1})]

        The field "k" in the dictionary (attr_dict) is set to 1. However, it is also
        provided as an argument but with the value 3. The latter is the one used to populate
        the edge attributes, which can be checked by printing the data of the edge (c.edges(data=True())


        .. seealso:: special attributes are automatically set by :meth:`set_default_edge_attributes`.
            the color of the edge is black if link is set to "+" and red otherwie.

        """
        link = Link(attr.get("link", "+"))
        attr['link'] = link.link

        attr = self.set_default_edge_attributes(**attr)

        # cast u to str to search for + sign
        if "+" in unicode(u):
            lhs = u.split("+")
            for x in lhs:
                if x.startswith("!"):
                    attr["link"] = "-"
                    attr['color'] = 'red'
                    attr['arrowhead'] = 'tee'
                    super(CNOGraph, self).add_edge(x[1:], v, attr_dict, **attr)
                else:
                    attr["link"] = "+"
                    super(CNOGraph, self).add_edge(x, v, attr_dict, **attr)
        else:
            super(CNOGraph, self).add_edge(u, v, attr_dict, **attr)

    def clear(self):
        """Remove nodes and edges and MIDAS instance"""
        super(CNOGraph, self).clear()
        self.midas = None
        self._stimuli = []
        self._signals = []
        self._inhibitors = []

    def clean_orphan_ands(self):
        """Remove AND gates that are not AND gates anymore

        When removing an edge or a node, AND gates may not be valid anymore
        either because the output does not exists or there is a single input.

        This function is called when :meth:`remove_node` or :meth:`remove_edge` are called.
        However, if you manipulate the nodes/edges manually you may need to call
        this function afterwards.
        """
        for node in self._find_and_nodes():
            if len(self.successors(node))==0 or len(self.predecessors(node))<=1:
                self.remove_node(node)
                continue

    def check_data_compatibility(self):
        """When setting a MIDAS file, need to check that it is compatible with
        the graph, i.e. species are found in the model."""
        if self.midas:
            msg = "The %s %s was found in the MIDAS file but is "
            msg += "not present in the model. Change your model or "
            msg += "MIDAS file."
            for x in self.midas.names_cues:
                if x not in self.nodes():
                    raise CNOError(msg % ('cues', x))
            for x in self.midas.names_signals:
                if x not in self.nodes():
                    raise CNOError(msg % ('signals', x))

    def remove_and_gates(self):
        """Remove the AND nodes added by :meth:`expand_and_gates`"""
        for n in self._find_and_nodes():
            self.remove_node(n)

    def __eq__(self, other):
        # we must look at the data to figure out the link + or - but should ignore
        # all other keys
        edges1 = sorted(self.edges(data=True))
        edges2 = sorted(other.edges(data=True))
        edges1  = [(e[0], e[1], {'link':e[2]['link']}) for e in edges1]
        edges2  = [(e[0], e[1], {'link':e[2]['link']}) for e in edges2]
        res = edges1 == edges2
        return res

    def __add__(self, other):
        """allows a+b operation

        combines the _inhibitors, _signals, _stimuli but keep only the first
        midas file !

        """
        G = self.copy()
        G.add_nodes_from(other.nodes(data=True))
        edges = other.edges(data=True)
        for e1,e2,d in edges:
            G.add_edge(e1,e2,None, **d)
        G._inhibitors += other._inhibitors
        G._signals += other._signals
        G._stimuli += other._stimuli

        # TODO: merge the MIDAS files. ?
        return G

    def __sub__(self, other):
        G = self.copy()
        G.remove_nodes_from([n for n in G if n in other.nodes()])
        return G

    def __str__(self):
        nodes = len([x for x in self.nodes() if '^' not in x])
        andnodes = len([x for x in self.nodes() if '^' in x])

        msg = "The model contains %s nodes (and %s AND node)\n" % (nodes, andnodes)

        self.logging.warning("Edge counting valid only if and node have only 2 inputs")
        edges = len([e for e in self.edges() if '^' not in e[0] and '^' not in e[1]])
        andedges = len([e for e in self.edges() if '^'  in e[0] or '^'  in e[1]])/3
        msg += "%s Hyperedges found (%s+%s) \n" % (edges+andedges, edges, andedges)

        return msg

    #def __rsub__(self, other):
    #    self.remove_nodes_from([n for n in self if n in other.nodes()])

    def union(self, other):
        """Return graph with elements from this instance and the input graph.

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            from pylab import subplot, title

            c1 = CNOGraph()
            c1.add_edge("A", "B", link="+")
            c1.add_edge("A", "C", link="-")
            c1.add_edge("C", "E", link="+")
            subplot(1,3,1)
            title(r"graph $C_1$")
            c1.plot(hold=True)

            c2 = CNOGraph()
            c2.add_edge("A", "B", link="+")
            c2.add_edge("B", "D", link="+")
            c2.add_edge("B", "F", link="+")
            subplot(1,3,2)
            c2.plot(hold=True)
            title(r"graph $C_2$")

            c3 = c1.union(c2)
            subplot(1,3,3)
            c3.plot(hold=True)
            title(r"graph $C_3 = C_1 \cup C_2$")

        """
        c = self + other
        return c

    def difference(self, other):
        """Return a CNOGraph instance that is the difference with the input graph

        (i.e. all elements that are in this set but not the others.)

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            from pylab import subplot, title

            c1 = CNOGraph()
            c1.add_edge("A", "B", link="+")
            c1.add_edge("A", "C", link="-")
            c1.add_edge("C", "E", link="+")
            subplot(1,3,1)
            title("graph C1")
            c1.plot(hold=True)

            c2 = CNOGraph()
            c2.add_edge("A", "B", link="+")
            c2.add_edge("B", "D", link="+")
            c2.add_edge("B", "F", link="+")
            subplot(1,3,2)
            c2.plot(hold=True)
            title("graph C2")

            c3 = c1.difference(c2)
            subplot(1,3,3)
            c3.plot(hold=True)
            title("graph C3=C1-C2")


        .. note:: this method should be equivalent to the - operator. So c1-c2 == c1.difference(c2)
        """
        G = self.copy()
        G.remove_nodes_from([n for n in G if n in other.nodes()])
        return G

    def intersect(self, other):
        """Return a graph with only nodes found in "other" graph.

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            from pylab import subplot, title

            c1 = CNOGraph()
            c1.add_edge("A", "B", link="+")
            c1.add_edge("A", "C", link="-")
            c1.add_edge("C", "E", link="+")
            subplot(1,3,1)
            title(r"graph $C_1$")
            c1.plot(hold=True)

            c2 = CNOGraph()
            c2.add_edge("A", "B", link="+")
            c2.add_edge("B", "D", link="+")
            c2.add_edge("B", "F", link="+")
            subplot(1,3,2)
            c2.plot(hold=True)
            title(r"graph $C_2$")

            c3 = c1.intersect(c2)
            subplot(1,3,3)
            c3.plot(hold=True)
            title(r"graph $C_3 = C_1 \cap C_2$")

        """
        G = self.copy()
        G.remove_nodes_from([n for n in G if n not in other])
        return G

    def draw(self, prog="dot", attribute="fillcolor",  hold=False, **kargs):
        """Draw the network using matplotlib. Not exactly what we want but could be useful.

        :param str prog: one of the graphviz program (default dot)
        :param bool hold: hold previous plot (default is False)
        :param str attribute: attribute to use to color the nodes (default is "fillcolor").
        :param node_size: default 1200
        :param width: default 2

        Uses the fillcolor attribute of the nodes
        Uses the link attribute of the edges

        .. seealso:: :meth:`plot` that is dedicated to this kind of plot using graphviz


        """
        self.logging.warning("Not for production. Use plot() instead")
        pos = nx.drawing.graphviz_layout(self, prog=prog)

        node_size = kargs.get('node_size', 1200)
        kargs['node_size'] = node_size

        width = kargs.get('width', 2)
        kargs['width'] = width

        # node attributes
        nodes = sorted(self.nodes())
        node_colors = [self.node[x][attribute] if attribute in self.node[x].keys()
                else "gray" for x in nodes]

        # edge attributes
        edges = self.edges(data=True)
        colors = {'-':'red', '+':'black'}
        edge_colors = [colors[x[2]['link']] for x in edges]

        nx.draw(self, prog=prog, hold=hold, nodelist=nodes,
            edge_color=edge_colors, node_color=node_colors,
            pos=pos, **kargs)

    def _check_dot_prog(self, prog):
        DevTools().check_param_in_list(prog, ["twopi", "gvcolor", "wc", "ccomps", "tred",
            "sccmap", "fdp", "circo", "neato", "acyclic", "nop", "gvpr", "dot",
            "sfdp"])

    def _get_cmap(self, cmap=None):
        if cmap == "heat":
            cmap = self._colormap.get_cmap_heat_r()
        elif cmap == "green":
            cmap = self._colormap.get_cmap_red_green()
        else:
            cmap = colormap.cmap_builder(cmap)
        return cmap

    def plot(self, prog="dot", viewer="pylab", hold=False, 
        show=True, filename=None, node_attribute=None, edge_attribute=None,
        cmap='heat', colorbar=False, remove_dot=True, 
        normalise_cmap=True, edge_attribute_labels=True, 
        rank_method='cno'
        ):
        """plotting graph using dot program (graphviz) and networkx

        By default, a temporary file is created to hold the image created by
        graphviz, which is them shown using pylab. You can choose not to see the
        image (show=False) and to save it in a local file instead (set the
        filename). The output format is PNG. You can play with
        networkx.write_dot to save the dot and create the SVG yourself.

        :param str prog: the graphviz layout algorithm (default is dot)
        :param viewer: pylab
        :param bool show: show the plot (True by default)
        :param bool remove_dot: if True, remove the temporary dot file.
        :param edge_attribute_labels: is True, if the label are available, show them.
            otherwise, if edge_attribute is provided, set lael as the edge_attribute

        :param rank_method: If none, let graphviz do the job. Issue is that (i)
            input stimuli may not be aligned and output neither. The rank_method set
            to **cno** constraints the stimuli and measured species that are sinks
            all others are free. The **same** constraint all nodes with same rank
            to be in the same subgraph.

        Additional attributes on the graph itself can be set up by populating the
        graph attribute with a dictionary called "graph"::

            c.graph['graph'] = {"splines":True, "size":(20,20), "dpi":200}

        Useful other options are::

            c.edge["tnfa"]["tnfr"]["penwidth"] = 3
            c.edge["tnfa"]["tnfr"]["label"] = " 5"

        If you use edge_attribute and show_edge_labels, label are replaced
        by the content of edge_attribute. If you still want differnt labels,
        you must stet show_label_edge to False and set the label attribute
        manually

        ::

            c = cnograph.CNOGraph()
            c.add_reaction("A=C")
            c.add_reaction("B=C")
            c.edge['A']['C']['measure'] = 0.5
            c.edge['B']['C']['measure'] = 0.1
            c.expand_and_gates()
            c.edge['A']['C']['label'] = "0.5 seconds"
            # compare this that shows only one user-defined label
            c.plot()
            # with that show all labels
            c.plot(edge_attribute="whatever", edge_attribute_labels=False)

        See the graphviz homepage documentation for more options.

        ::

            c.plot(filename='test.svg', viewer='yout_favorite_viewer',  
                remove_dot=False, rank_method='cno')


        .. note:: edge attribute in CNOGraph (Directed Graph) are not coded
            in the same way in CNOGraphMultiEdges (Multi Directed Graph).
            So, this function does not work for MultiGraph

        .. todo:: use same colorbar as in midas. rigtht now; the vmax is not correct.
        .. todo:: precision on edge_attribute to 2 digits.

        if filename provided with extension different from png, pylab must be able to 
        read the image. If not, you should set viewer to something else.

        """
        # graph is a DiGraph attribute
        # that is sometimes replaced by {} inside networkx so we need to overwrite it here
        # each time we want to plot the graph.
        if len(self)==0:
            self.logging.error("empty graph, nothing to plot")
            return

        self._check_dot_prog(prog)

        # Get the default/user attributes for the graph/nodes/edges for graphviz
        self.graph = self.graph_options.copy()

        # Set the colormap
        cmap = self._get_cmap(cmap)
         
        # update the node attributes if required with default color
        # or ues the requried node attribute. 
        M = 1
        if node_attribute == None:
            self.set_default_node_attributes()
        else:
            # TODO check that it exists
            #cmap = matplotlib.cm.get_cmap(cmap)
            sm = matplotlib.cm.ScalarMappable(
                norm = matplotlib.colors.Normalize(vmin=0, vmax=1), cmap=cmap)

             # node[0] is the name, node[1] is the data
            data = [node[1][node_attribute] for node in self.nodes(data=True) 
                    if node_attribute in node[1].keys()]
            if normalise_cmap == True:
                M = max(data)

            # color could be encoded as values between 0 and 1
            # or hexa. Default to 1. If not all are provided, 
            # no errors raised.
            for node in self.nodes():
                # default
                self.node[node]['fillcolor'] = "#FFFFFF"
                try:
                    value = self.node[node][node_attribute]/float(M)
                    rgb = sm.to_rgba(value)
                    colorHex = matplotlib.colors.rgb2hex(rgb)
                    self.node[node]['fillcolor'] = colorHex
                except:
                    try:
                        color = self.node[node][node_attribute]
                        self.node[node]['fillcolor'] = colormap.Color(color).hex
                    except:
                        pass

        # update the edge attribute
        if edge_attribute:
            M = self._set_edge_attribute_color(edge_attribute, cmap)

        # create temp files
        # FIXME we create png here ?? do we use outfile ?
        infile  = tempfile.NamedTemporaryFile(suffix=".dot", delete=False)
        if filename == None:
            outfile  = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            filename = outfile.name

        # Some nodes may belong to 2 colors. Creating subgraph is one way to go
        # around. Having graphviz 2.30 we could use striped node.
        if node_attribute is None:
            for node in self.nodes():
                if node in self.signals and node in self.inhibitors:
                    self.node[node]['style'] = "diagonals,filled"
                    self.node[node]['color'] = "red"
                    self.node[node]['fillcolor'] = "lightblue"
                if node in self.stimuli and node in self.inhibitors:
                    self.node[node]['style'] = "diagonals,filled"
                    self.node[node]['color'] = "red"
                    self.node[node]['fillcolor'] = "#9ACD32"


        # to not change the current graph, let us copy it
        # FIXME we use 'this' variable  and use it for edges
        # but not for the nodes... why ?
        this = self.copy()

        if edge_attribute_labels and edge_attribute != None:
            self._set_edge_attribute_label(this, edge_attribute)

        count = 0
        ret = -1
        while count < 10:
            H = self._get_ranked_agraph(rank_method)            
            H.write(infile.name)
            frmt = os.path.splitext(filename)[1][1:]
            try:
                if filename.endswith('svg') and 'dpi' in H.graph_attr.keys():
                    del H.graph_attr['dpi']
                #just to try
                H.draw(path=filename, prog=prog, format=frmt)
                count = 1000
                ret = 0
            except Exception as err:
                print(err.message)
                self.logging.warning("%s program failed. Trying again" % prog)
                count += 1

        if ret !=0:
            if rank_method is not None:
                self.logging.warning("%s program failed to create image" % prog)
            H = nx.to_agraph(this)
            if filename.endswith('svg') and 'dpi' in H.graph_attr.keys():
                del H.graph_attr['dpi']
            frmt = os.path.splitext(filename)[1][1:]
            H.draw(path=filename, prog=prog, format=frmt)


        # Here is the visualisation only iif image was created
        if viewer=="pylab" and show is True:
            if hold == False:
                if hold is False:
                    pylab.clf()
                f = pylab.gcf()
                f.set_facecolor("white")
                a = f.add_axes([0.05,0.04,0.8,0.9])
                a.imshow(pylab.imread(filename))
                a.axis('off')
            else:
                a = pylab.imshow(pylab.imread(filename))
                pylab.axis('off')

            if colorbar:
                cbar = pylab.linspace(0, 1, 100)
                e = f.add_axes([.86, .05, .05, .9])
                e.pcolor(pylab.array([cbar, cbar]).transpose(),
                        cmap=cmap, vmin=0, vmax=1);
                e.yaxis.tick_right()
                e.set_xticks([],[])

                e.set_yticks([0,20,40,60,80,100])
                if normalise_cmap is True:
                    # TODO precision for small number ??
                    from easydev.tools import precision
                    e.set_yticklabels([precision(x,3) for x in pylab.linspace(0, M, 6)])
                else:
                    e.set_yticklabels([0, 0.2, 0.4, 0.6, 0.8, 1])
                    
        elif show is True:
            subprocess.call("%s %s &" % (viewer, filename), shell=True)

        if remove_dot == True:
            infile.delete = True
            infile.close()
        else:
            print("Creating dot file named 'model.dot'")
            shutil.move(infile.name, "model.dot")
            infile.close()

        if filename == False:
            outfile.delete = True
            outfile.close()

        if node_attribute != None:
            self.set_default_node_attributes()

        #if show == True:
        #    try:
        #        from biokit.dev.mpl_focus import ZoomPan
        #        ax = pylab.gca()
        #        zp = ZoomPan()
        #        _ = zp.zoom_factory(ax, base_scale = 1.2)
        #        _ = zp.pan_factory(ax)
        #    except:
        #        pass

    def _plot_rmse_fromR(self, filename, F=.3, scale=2, col=None):
        """
        filename should be a CSV with first column being node names and second
        column the values.

        This function populates the node attribute "mse", which should be the
        average RMSE over all experiment for each species.

        :param col: if col is None, average all columns

        c.plot()
        """
        import pandas as pd
        df = pd.read_csv(filename, index_col=0,  header=None)

        if col==None:
            df = df.mean(axis=1)
        elif col in df.columns:
            df = df[col]
        else:
            print("Invalid column provided. Use one of {}".format(df.columns))
        for this in self.nodes():
            if this in self.signals:
                mse = df.ix[this] #.values[0]
                self.node[this]['mse'] =  (1-(mse/F)**scale)
                self.node[this]['label'] =  this+"\n"+unicode(int(mse*1000)/1000.)
            else:
                self.node[this]['mse'] = 1
        cm = colormap.Colormap()
        self.plot(node_attribute="mse", cmap=cm.get_cmap_heat())

    def _set_edge_attribute_label(self, this, edge_attribute):
        for e in this.edges():
            this.edge[e[0]][e[1]]['label'] = this.edge[e[0]][e[1]][edge_attribute]

    def _set_edge_attribute_color(self, edge_attribute, cmap):
        import matplotlib
        cmap = matplotlib.cm.get_cmap(cmap)
        sm = matplotlib.cm.ScalarMappable(
            norm=matplotlib.colors.Normalize(vmin=0, vmax=1), cmap=cmap)

        M = max([self.edge[edge[0]][edge[1]][edge_attribute] for edge in self.edges()])

        for edge in self.edges():
            value = self.edge[edge[0]][edge[1]][edge_attribute]/float(M)
            rgb = sm.to_rgba(value)
            colorHex = matplotlib.colors.rgb2hex(rgb)
            self.edge[edge[0]][edge[1]]['color'] = colorHex
        return M

    def _get_ranked_agraph(self, rank_method=None):
        """and gates should have intermediate ranks"""
        H = nx.to_agraph(self)

        for k, v in self.graph_options['graph'].iteritems():
            H.graph_attr[k] = v
        for k, v in self.graph_options['edge'].iteritems():
            H.edge_attr[k] = v
        for k, v in self.graph_options['node'].iteritems():
            H.edge_attr[k] = v

        if rank_method is None:
            return H 
        if self.midas is None:
            return H

        # order the graph for ranks
        allranks = self.get_same_rank() # this has been checkd on MMB to
        ranks  = {}
        M = max(allranks.keys())
        for k, v in allranks.iteritems():
            ranks[k] = sorted([x for x in v if '=' not in x],
                    cmp=lambda x,y:cmp(x.lower(), y.lower()))
            # add invisible edges so that the nodes that have the same rank are
            # ordered.
            if k == 0:
                for i, node1 in enumerate(ranks[k]):
                    if i != len(ranks[k])-1:
                        node2 = ranks[k][i+1]
                        H.add_edge(node1, node2, style="invis")
            if k == M:
                for i, node1 in enumerate(ranks[k]):
                    if i != len(ranks[k])-1:
                        node2 = ranks[k][i+1]
                        H.add_edge(node1, node2, style="invis")
            
        # Note: if name is set to "cluster"+name, black box is put around the cluster
        for rank in sorted(ranks.keys()):
            name = unicode(rank)
            if rank == 0:
                # label will be used if name == 'cluster_source'
                H.add_subgraph(ranks[rank],  rank='source', name='source', 
                        label='stimuli')
            elif rank == M:
                H.add_subgraph(ranks[rank], name="sink", rank='sink')
            else:
                if rank_method == "same":
                    H.add_subgraph(ranks[rank], name=name, rank='same')
        return H

    def _get_nonc(self):
        if self._nonc is None:
            nonc = self.findnonc()
            self._nonc = nonc
        return self._nonc
    nonc = property(fget=_get_nonc,
        doc="Returns list of Non observable and non controlable nodes (Read-only).")

    def _get_reactions(self):
        sif = self.to_sif()
        return sif.reactions
    reactions = property(_get_reactions, doc="return the reactions (edges)")

    def _get_namesSpecies(self):
        nodes = self.nodes()
        nodes = [x for x in nodes if "+" not in x and "=" not in x]
        return sorted(nodes)
    species = property(fget=_get_namesSpecies,
        doc="Return sorted list of species (ignoring and gates) Read-only attribute.")

    def swap_edges(self, nswap=1, inplace=True):
        """Swap two edges in the graph while keeping the node degrees fixed.

        A double-edge swap removes two randomly chosen edges u-v and x-y
        and creates the new edges u-x and v-y::

            u--v                u  v
                    becomes     |  |
            x--y                x  y

        If either the edge u-  x or v-y already exist no swap is performed
        and another attempt is made to find a suitable edge pair.

        :param int nswap: number of swaps to perform (Defaults to 1)
        :return: nothing

        .. warning:: the graph is modified in place.

        .. warning:: and gates are currently unchanged

        a proposal swap is ignored in 3 cases:
        #. if the summation of in_degree is changed
        #. if the summation of out_degree is changed
        #. if resulting graph is disconnected

        """
        Ninh = [x[2]["link"] for x in self.edges(data=True)].count('-')
        I = sum(self.in_degree().values())
        O = sum(self.out_degree().values())

        # find 2 nodes that have at least one successor
        count = 0
        for i in range(0, nswap):
            #print(i)
            edges = self.edges()
            np.random.shuffle(edges)
            e1, e2 = edges[0:2]
            if "^" in e1[0] or "^" in e1[1] or "^" in e2[0] or "^" in e2[1]:
                continue
            d1 = self.edge[e1[0]][e1[1]].copy()
            d2 = self.edge[e2[0]][e2[1]].copy()

            G = self.copy()
            G.add_edge(e1[0], e2[1], None, **d1)
            G.add_edge(e2[0], e1[1], None, **d2)
            G.remove_edge(e1[0], e1[1])
            G.remove_edge(e2[0], e2[1])

            if nx.is_connected(G.to_undirected()) == False:
                #print("G is disconnected.skipping------")
                continue
            if sum(G.in_degree().values()) != I:
                # the link already exists
                continue

            if sum(G.out_degree().values()) != O:
                continue

            self.add_edge(e1[0], e2[1], None, **d1)
            self.add_edge(e2[0], e1[1], None, **d2)
            self.remove_edge(e1[0], e1[1])
            self.remove_edge(e2[0], e2[1])

            Ninh2 = [x[2]["link"] for x in self.edges(data=True)].count('-')
            assert Ninh2 == Ninh

            assert nx.is_connected(self.to_undirected()) == True
            count +=1
        print("swap %d edges" % count)

    def adjacency_matrix(self, nodelist=None, weight=None):
        """Return adjacency matrix.

        :param list nodelist: The rows and columns are ordered according to the nodes in nodelist.
            If nodelist is None, then the ordering is produced by :meth:`nodes` method.

        :param str weight: (default=None) The edge data key used to provide each value in the matrix.
            If None, then each edge has weight 1. Otherwise, you can set it to
            "weight"

        :returns: numpy matrix Adjacency matrix representation of CNOGraph.

        .. note:: alias to :meth:`networkx.adjacency_matrix`

        .. seealso:: :meth:`adjacency_iter` and :meth:`adjacency_list`

        """
        return nx.adjacency_matrix(self, nodelist=nodelist).astype(int)

    def remove_edge(self, u, v):
        """Remove the edge between u and v.

        :param str u: node u
        :param str u: node v

        Calls :meth:`clean_orphan_ands` afterwards
        """
        super(CNOGraph, self).remove_edge(u,v)
        #if "+" not in n:
        self.clean_orphan_ands()

    def remove_node(self, n):
        """Remove a node n

        :param str node: the node to be removed

        Edges linked to **n** are also removed. **AND** gate may now be
        irrelevant (only one input or no input). Orphan AND gates are removed.

        .. seealso:: :meth:`clean_orphan_ands`

        """
        super(CNOGraph, self).remove_node(n)
        if "^" not in unicode(n):
            self.clean_orphan_ands()

    def add_node(self, node, attr_dict=None, **attr):
        """Add a node

        :param str node: a node to add
        :param dict attr_dict: dictionary, optional (default= no attributes)
             Dictionary of edge attributes.  Key/value pairs will update existing
             data associated with the edge.
        :param attr: keyword arguments, optional
            edge data (or labels or objects) can be assigned using keyword arguments.
            keywords provided will overwrite keys provided in the **attr_dict** parameter

        .. warning:: color, fillcolor, shape, style are automatically set.


        ::

            c = CNOGraph()
            c.add_node("A", data=[1,2,3,])

        .. warning:: **attr** replaces any key found in attr_dict. See :meth:`add_edge` for details.

        .. todo:: currently nodes that contains a ^ sign are interpreted as AND gate and will appear
           as small circle. One way to go around is to use the label attribute.
           you first add the node with a differnt name and populate the label with
           the correct nale (the one that contain the ^ sign); When calling the plot
           function, they should all appear as expected.

        """
        if attr_dict:
            print("Warning: attr_dict overwritten")

        if "fillcolor" not in attr.keys():
            attr["fillcolor"] = "white"
        attr_dict = self.get_node_attributes(node)
        if "fillcolor" not in attr_dict.keys():
            attr_dict["fillcolor"] = "white"
            attr["fillcolor"] = "white"
        super(CNOGraph, self).add_node(node, attr_dict, **attr)

    def preprocessing(self, expansion=True, compression=True, cutnonc=True,
                      maxInputsPerGate=2):
        """Performs the 3 preprocessing steps (cutnonc, expansion, compression)

        :param bool expansion: calls :meth:`expand_and_gates` method
        :param bool compression: calls :meth:`compress` method
        :param bool cutnon: calls :meth:`cutnonc` method
        :param int maxInputPerGates: parameter for the expansion step

        .. plot::
            :width: 80%
            :include-source:

            from cno import CNOGraph, cnodata
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.preprocessing()
            c.plot()

        """
        if cutnonc:
            self.cutnonc()
        if compression:
            self.compress()
        if expansion:
            self.expand_and_gates(maxInputsPerGate=maxInputsPerGate)

    def cutnonc(self):
        """Finds non-observable and non-controllable nodes and removes them.

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph, cnodata
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.cutnonc()
            c.plot()

        """
        nonc = self.nonc[:]
        for node in nonc:
            self.collapse_node(node)

    def compress(self, recursive=True, iteration=1, max_iteration=5):
        """Finds compressable nodes and removes them from the graph

        A compressable node is a node that is not part of the special nodes
        (stimuli/inhibitors/readouts mentionned in the MIDAS file). Nodes
        that have multiple inputs and multiple outputs are not compressable
        either.


        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph, cnodata
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.cutnonc()
            c.compress()
            c.plot()



        .. seealso:: :meth:`compressable_nodes`, :meth:`is_compressable`
        """
        assert max_iteration >=1
        #Patched to proceed on sorted lists and provide always the same results.
        #for node in self.compressable_nodes:
        for node in sorted(self.compressable_nodes):
            if self.is_compressable(node) == True:
                # update the graph G as well and interMat/notMat
                self._compressed.append(node)
                self.collapse_node(node)
                #self.midas.cnolist.namesCompressed.append(node)

        #Patched to proceed on a sorted list and provide always the same results.
        #for node in self.nodes():
        for node in sorted(self.nodes()):
            if self.degree(node) == 0 and node not in self.stimuli and \
                node not in self.signals and node not in self.inhibitors:
                """
                FIXME It consists in finding the list of nodes that belong
                to the network but are in no edges (if a node A is
                removed during compression, it appears in no edges,
                but you can still find it in CNOGraph.nodes()). For
                this set of nodes that do not belong to the network,
                I add fake edges like A + mock1 and so on.

                Doing like this I am able to save the compressed (or
                the repaired) network, while using the same MIDAS file.

                I was afraid to touch the code because I am not sure
                whether this is the intended behaviour."""

                self.logging.info("Found an orphan, which has been removed (%s)" % node)
                self.remove_node(node)

        if len(self.compressable_nodes) > 0:
            self.logging.warning("There are still compressable nodes. Call again")
            if recursive and iteration<max_iteration:
                self.compress(iteration=iteration+1)

    def _get_collapse_edge(self, inputAttrs, outputAttrs):
        attrs = inputAttrs.copy()
        if inputAttrs['link'] == outputAttrs['link']:
            attrs['link'] = "+"
            attrs['color'] = "black"
            attrs['arrowhead'] = "normal"
        else:
            attrs['link'] = "-"
            attrs['color'] = "red"
            attrs['arrowhead'] = "tee"

        return attrs

    def collapse_node(self, node):
        """Collapses a node (removes a node but connects input nodes to output nodes)

        This is different from :meth:`remove_node`, which removes a node and its edges thus
        creating non-connected graph. :meth:`collapse_node`, instead remove the node but merge the input/output
        edges IF possible. If there are multiple inputs AND multiple outputs the
        node is not removed.

        :param str node: a node to collapse.

        * Nodes are collapsed if there is at least one input or output.
        * Node are not removed if there is several inputs and several ouputs.
        * if the input edge is -, and the next is + or viceversa then the final edge if -
        * if the input edge is - and output is - then final edge is +

        """
        # Removing a node that has several entries and several outputs is not
        # implemented because there is no such situation in CNO.
        successors = self.successors(node)
        predecessors = self.predecessors(node)

        # todo: may be simplified ?
        if len(successors) == 1 and len(predecessors)==1:
            self.logging.debug("Compressing %s 1,1 mode" % node)
            # compressed node
            attr1 = self.edge[node][successors[0]]
            #
            attr2 = self.edge[predecessors[0]][node]

            attrs = self._get_collapse_edge(attr1, attr2)
            if predecessors[0] != successors[0]:
                self.add_edge(predecessors[0], successors[0], None, **attrs)
        elif len(successors) == 1:

            for predecessor in predecessors:
                attr = self.edge[predecessor][node]
                if predecessor != successors[0]:
                    attr2 = self.edge[node][successors[0]]
                    attrs = self._get_collapse_edge(attr, attr2)
                    self.add_edge(predecessor, successors[0], None, **attrs)
        elif len(predecessors) == 1:
            for successor in successors:
                attr = self.edge[node][successor]
                if predecessors[0] != successor:
                    attr2 = self.edge[predecessors[0]][node]
                    attrs = self._get_collapse_edge(attr, attr2)
                    self.add_edge(predecessors[0], successor, None,  **attrs)
        else:
            if len(successors) > 1 and len(predecessors) > 1:
                self.logging.debug(node, successors, predecessors)
                self.logging.warning("N succ >1 and N pred >1. Node not removed. use remove_node() if you really want to remove it")
                return
                #raise ValueError("invalid node to remove several in/out")
            else:
                self.logging.debug("%s %s %s" % (node, successors, predecessors))
                self.logging.warning("unknown case (no output or input ?). Node %s removed"% node)
                #raise ValueError("invalid node to remove several in/out")
        self.remove_node(node)

    def get_node_attributes(self, node):
        """Returns attributes of a node using the MIDAS attribute

        Given a node, this function identifies the type of the input
        node and returns a dictionary with the relevant attributes found
        in :attr:`node_attributes.attributes`.

        For instance, if a midas file exists and if **node** belongs to the stimuli,
        then the dicitonary returned contains the color green.

        :param str node:
        :returns: dictionary of attributes.

        """
        # default
        attr = self.attributes['others'].copy()
        # otherwisen
        if self.midas:
            if node in self.stimuli:
                attr = self.attributes['stimuli'].copy()
            elif node in self.signals:
                attr = self.attributes['signals'].copy()
            elif node in self.inhibitors:
                attr = self.attributes['inhibitors'].copy()
            elif node in self.nonc: # or node in self.findnonc():
                attr = self.attributes['nonc'].copy()
            elif '^' in node:
                attr = self.attributes['and'].copy()
            elif node in self.compressable_nodes:
                attr = self.attributes['compressed'].copy()
        else:
            if '^' in unicode(node):
                attr = self.attributes['and'].copy()

        if node in self._stimuli:
            attr = self.attributes['stimuli'].copy()
        if node in self._signals:
            attr = self.attributes['signals'].copy()
        if node in self._inhibitors:
            attr = self.attributes['inhibitors'].copy()
        return attr

    def predecessors_as_reactions(self, node):
        """Build up reactions for a given node from predecessors only"""
        predecessors = self.predecessors(node)
        reactions = []
        for pred in predecessors:
            if self.isand(pred):
                reactions.append(pred)
            elif self[pred][node]['link'] == '+':
                reactions.append(pred + "=" +node)
            else:
                reactions.append("!" + pred + "=" +node)
        return reactions

    def set_default_node_attributes(self):
        """Set all node attributes to default attributes

        .. seealso:: :meth:`get_node_attributes`
        """
        for node in self.nodes():
            attrs = self.get_node_attributes(node)
            for k,v in attrs.iteritems():
                self.node[node][k] = v

    def get_same_rank(self):
        """Return ranks of the nodes.

        Used by plot/graphviz. Depends on attribute :attr:`dot_mode`

        """
        self.dot_mode = "end_signals_bottom"
        # some aliases
        try:
            stimuli = self.stimuli
            if len(stimuli) == 0:
                stimuli = self._get_inputs()
        except:
            stimuli = self._get_inputs()

        try:
            signals = self.signals
            if len(signals) == 0:
                signals = self._get_outputs()
        except:
            signals = self._get_outputs()

        func_path = nx.algorithms.floyd_warshall(self)

        maxrank = int(self.get_max_rank())
        # start populating the ranks starting with the obvious one: stimuli and
        # signals
        ranks = {}
        ranks[0] = stimuli
        for i in range(1, maxrank+1):
            ranks[i] = []

        if self.dot_mode == 'free':
            """default layout but stimuli on top"""
            for node in self.nodes():
                if node not in stimuli:
                    distances = [func_path[s][node] for s in stimuli]
                    distances = [abs(x) for x in distances if x != pylab.inf]
                    if len(distances) != 0:
                        M = pylab.nanmin([x for x in distances if x != pylab.inf])
                        try:
                            ranks[M].append(node)
                        except:
                            ranks[M] = [node]
                    else:
                        self.logging.debug('warning, rank %s is empyt'% node)

        elif self.dot_mode == 'end_signals_bottom':
            maxrank = max(ranks.keys())
            ranks[maxrank+1] = []

            for node in sorted(self.nodes(), 
                    cmp=lambda x,y: cmp(unicode(x).lower(), unicode(y).lower())):
                # skip and gate
                if self.isand(node):
                    continue
                # skip end signals
                if node in signals and len(self.successors(node))==0:
                    continue
                elif node not in stimuli:
                    distances = [func_path[s][node] for s in stimuli]
                    distances = [x for x in distances if x != pylab.inf]
                    if len(distances) != 0:
                        M = np.nanmax([abs(x) for x in distances if x != pylab.inf])
                        try:
                            ranks[M].append(node)
                        except:
                            ranks[M] = [node]
                    else:
                        self.logging.debug('warning, rank %s is empyt'% node)

            for node in sorted(self.nodes(), 
                    cmp=lambda x,y: cmp(unicode(x).lower(),unicode(y).lower())):

                if node in signals and len(self.successors(node))==0:
                    try:
                        # +1 so that signals are alone on their row without nonc
                        ranks[maxrank+1].append(node)
                    except:                       
                        ranks[maxrank] = [node]
        return ranks

    def _get_inputs(self):
        return [x for x in self.nodes() if len(self.predecessors(x))==0]

    def _get_outputs(self):
        self.logging.warning('WARNING. no signals found, tryring to build a list (node with no successors)')
        return  [x for x in self.nodes() if len(self.successors(x))==0]

    def get_max_rank(self):
        """Get the maximum rank from the inputs using floyd warshall algorithm

        If a MIDAS file is provided, the inputs correspond to the stimuli.
        Otherwise, (or if there is no stimuli in the MIDAS file),
        use the nodes that have no predecessors as inputs (ie, rank=0).

        """
        stimuli = self.stimuli
        if len(stimuli) == 0:
            stimuli = self._get_inputs()

        func_path = nx.algorithms.floyd_warshall(self)
        # compute the longest path from Stimuli by using the floyd warshall
        # algorithm. inputs/stimuli has rank 0.
        ranks = [[x for x in func_path[stimulus].values() if x !=pylab.inf]
            for stimulus in stimuli]

        allranks = []
        for r in ranks:
            allranks = allranks + r #concatenate all ranks includeing empty []
        maxrank = np.nanmax(allranks)
        return maxrank

    def _add_and_gates(self, node, maxInputsPerGate=2):
        """See expand_and_gates docstring"""
        preds = self.predecessors(node)
        preds = [pred for pred in preds if self.isand(pred) is False]
        assert maxInputsPerGate>=2 and maxInputsPerGate<=5, "maxInputsPerGate must be >2 and less than 5"
        #todo: order predecessirs according to nameSpecies order
        self.logging.debug( "node %s, pred=%s " % (node,  preds))

        if len(preds) == 1:
            self.logging.debug("Nothing to do with %s (only 1 predecessor)" % node)
            return

        for inputsPerGates in range(2, maxInputsPerGate+1):
            self.logging.debug(inputsPerGates)
            if inputsPerGates>len(preds):
                continue
            for combi in itertools.combinations(preds, inputsPerGates):
                self.logging.debug("adding %s input gate from %s to %s" % (inputsPerGates, combi, node))
                shape = "circle"
                if len(combi) == 3:
                    shape = "triangle"
                elif len(combi) >= 4:
                    shape = "square"
                andNode = self._nodes2reac(list(combi), node)
                self.logging.debug("add_and_gates: %s " % andNode)
                self.add_node(andNode, shape=shape)
                for combinode in combi:
                    attr = self.edge[combinode][node].copy()
                    attr['link'] = self.edge[combinode][node]['link']
                    #attr['weight'] = pylab.nan # edge from and to specy always + and nan weight
                    self.add_edge(combinode, andNode, None, **attr)
                attr['link'] = "+" # edge from and to specy always +
                #attr['weight'] = pylab.nan # edge from and to specy always + and nan weight
                attr['color'] = 'black' # and output is always black
                self.add_edge(andNode, node, None, **attr)

    def _nodes2reac(self, inputsNodes, output):
        inputs = []
        for node in inputsNodes:
            if self.edge[node][output]['link']=="-":
                inputs.append("!"+node)
            else:
                inputs.append(node)

        reac = self.and_symbol.join([unicode(x) for x in inputs])
        reac += "=" + unicode(output)
        print(reac)
        # FIXME: what aboit sorting while doing the instanciation.
        reac = Reaction(reac)
        reac.sort()
        return reac.name

    def isand(self, node):
        if self.and_symbol in unicode(node):
            return True
        else:
            return False

    def _find_nodes_with_multiple_inputs(self):
        """return a list of nodes that have multiple predecessors"""
        nodes = []
        for node in self.nodes():
            if len(self.predecessors(node)) > 1 and self.isand(node) is False:
                nodes.append(node)
            else:
                if len(self.predecessors(node)) > 1 and self.isand(node):
                    self.logging.debug("ignore ", node)
        return nodes

    def _find_and_nodes(self):
        andNodes = [node for node in self.nodes() if self.isand(node)]
        return andNodes

    def expand_or_gates(self):
        """Expand OR gates given AND gates

        If a graph contains AND gates (without its OR gates), you can add back
        the OR gates automatically using this function.

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            from pylab import subplot, title

            c1 = CNOGraph()
            c1.add_edge("A", "C", link="-")
            c1.add_edge("B", "C", link="+")
            c1.expand_and_gates()
            subplot(1,3,1)
            title("OR and AND gates")
            c1.plot(hold=True)

            c1.remove_edge("A", "C")
            c1.remove_edge("B", "C")
            subplot(1,3,2)
            c1.plot(hold=True)
            title("AND gates only")

            c1.expand_or_gates()
            subplot(1,3,3)
            c1.plot(hold=True)
            title("after call to \\n expand_or_gates function")

        .. seealso:: :meth:`~cno.io.cnograph.CNOGraph.expand_and_gates`

        """
        for this in self._find_and_nodes():
            p = self.predecessors(this)
            s = self.successors(this)
            assert len(s) == 1
            for node in p:
                link = self.edge[node][this]['link']
                self.add_edge(node, s[0], link=link)

    def expand_and_gates(self, maxInputsPerGate=2):
        """Expands the network to incorporate AND gates

        :param int maxInputsPerGate: restrict maximum number of inputs used to
            create AND gates (default is 2)

        The CNOGraph instance can be used to model a boolean network.  If a node
        has several inputs,  then the combinaison of the inputs behaves like an OR gate
        that is we can take the minimum over the inputs.

        In order to include AND behaviour, we introduce a special node called
        AND gate. This function adds AND gates whenever a node has several
        inputs. The AND gates can later on be used in a boolean formalism.

        In order to recognise AND gates, we name them according to the following
        rule. If a node A has two inputs B and C, then the AND gate is named::

            B^C=A

        and 3 edges are added: B to the AND gates, C to the AND gates and the AND gate to A.

        If an edge is a "-" link then, an **!** character is introduced.

        In this expansion process, AND gates themselves are ignored.

        If there are more than 2 inputs, all combinaison of inputs may be
        considered but the default parameter **maxInputsPerGate** is set to 2.
        For instance, with 3 inputs A,B,C you may have the
        following combinaison: A^B, A^C, B^C. The link A^B^C will be added only
        if **maxInputsPerGate** is set to 3.


        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            from pylab import subplot, title

            c = CNOGraph()
            c.add_edge("A", "C", link="+")
            c.add_edge("B", "C", link="+")
            subplot(1,2,1)
            title("Original network")
            c.plot(hold=True)

            c.expand_and_gates()
            subplot(1,2,2)
            c.plot(hold=True)
            title("Expanded network")

        .. seealso:: :meth:`remove_and_gates`, :meth:`clean_orphan_ands`,
            :meth:`expand_or_gates`.

        .. note:: this method adds all AND gates in one go. If you want to add a specific AND gate,
            you have to do it manually. You can use the :meth:`add_reaction` for that purpose.


        .. note:: propagate data from edge on the AND gates.
        """
        nodes2expand = self._find_nodes_with_multiple_inputs()
        for node in nodes2expand:
            self._add_and_gates(node, maxInputsPerGate)

    def add_cycle(self, nodes, **attr):
        """Add a cycle

        :param list nodes: a list of nodes. A cycle will be constructed from
           the nodes (in order) and added to the graph.
        :param dict attr: must provide the "link" keyword. Valid values are "+", "-"
            the links of every edge in the cycle will be identical.

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            c = CNOGraph()
            c.add_edge("A", "C", link="+")
            c.add_edge("B", "C", link="+")
            c.add_cycle(["B", "C", "D"], link="-")
            c.plot()

        .. warning:: added cycle overwrite previous edges

        """

        if "link" not in attr.keys():
            raise KeyError("link keyword must be provided")

        attr = self.set_default_edge_attributes(**attr)
        super(CNOGraph, self).add_cycle(nodes, **attr)

    def add_path(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def add_star(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def remove_edges_from(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def add_weighted_edges_from(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        """add list of edges with same parameters

        ::

            c.add_edges_from([(0,1),(1,2)], data=[1,2])

        .. seealso:: :meth:`add_edge` for details.

        """
        super(CNOGraph, self).add_edges_from(ebunch, attr_dict=None, **attr)
        #for e in ebunch:
        #    self.add_edge(e[0], e[1], attr_dict=attr_dict, **attr)

    def add_nodes_from(self, nbunch, attr_dict=None, **attr):
        """Add a bunch of nodes

        :param list nbunch: list of nodes. Each node being a string.
        :param dict attr_dict: dictionary, optional (default= no attributes)
             Dictionary of edge attributes.  Key/value pairs will update existing
             data associated with the edge.
        :param attr: keyword arguments, optional
            edge data (or labels or objects) can be assigned using keyword arguments.
            keywords provided will overwrite keys provided in the **attr_dict** parameter

        .. warning:: color, fillcolor, shape, style are automatically set.

        .. seealso:: :meth:`add_node` for details.


        """
        super(CNOGraph, self).add_nodes_from(nbunch, attr_dict=None, **attr)
        #for n in nbunch:
        #    self.add_node(n, attr_dict=attr_dict, **attr)

    def remove_nodes_from(self, nbunch):
        """Removes a bunch of nodes

        .. warning:: need to be tests with and gates."""
        super(CNOGraph, self).remove_nodes_from(nbunch)

    def _get_compressable_nodes(self):
        compressables = [x for x in self.nodes() if self.is_compressable(x)]
        if self._compress_ands == True:
            return compressables
        else:
            return [x for x in compressables if self.isand(x) is False]
    compressable_nodes = property(fget=_get_compressable_nodes,
        doc="Returns list of compressable nodes (Read-only).")

    def _ambiguous_multiedge(self, node):
        """Test whether the removal of a node may lead to multi edges ambiguity

        e.g., A-->B and A--| B
        """
        edges = [(x[0], x[1], x[2]['link']) for x in self.edges(data=True)]
        for A in self.predecessors(node):
            for B in self.successors(node):
                link = self.edge[node][B]['link']
                if link == "+": 
                    link = "-"
                elif link == "-": 
                    link = "+"
                if (A, B, link) in edges:
                    return True
        return False

    def is_compressable(self, node):
        """Returns True if the node can be compressed, False otherwise

        :param str node: a valid node name
        :return: boolean value

        Here are the rules for compression. The main idea is that a node can be removed if the
        boolean logic is preserved (i.e. truth table on remaining nodes is preserved).

        A node is compressable if it is not part of the stimuli, inhibitors, or
        signals specified in the MIDAS file.

        If a node has several outputs and inputs, it cannot be compressed.

        If a node has one input or one output, it may be compressed.
        However, we must check the following possible ambiguity that could be raised by the removal
        of the node: once removed, the output of the node may have multiple input edges with different
        types of inputs edges that has a truth table different from the original truth table.
        In such case, the node cannot be compressed.

        Finally, a node cannot be compressed if one input is also an output (e.g., cycle).


        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            from pylab import subplot,show, title
            c = cnograph.CNOGraph()
            c.add_edge("a", "c", link="-")
            c.add_edge("b", "c", link="+")
            c.add_edge("c", "d", link="+")
            c.add_edge("b", "d", link="-")
            c.add_edge("d", "e", link="-")
            c.add_edge("e", "g", link="+")
            c.add_edge("g", "h", link="+")
            c.add_edge("h", "g", link="+")

            # multiple inputs/outputs are not removed
            c.add_edge("s1", "n1", link="+")
            c.add_edge("s2", "n1", link="+")
            c.add_edge("n1", "o1", link="+")
            c.add_edge("n1", "o2", link="+")

            c._stimuli = ["a", "b", "s1", "s2"]
            c._signals = ["d", "g", "o1", "o2"]

            subplot(1,2,1)
            c.plot(hold=True)
            title("Initial graph")

            c.compress()
            subplot(1,2,2)
            c.plot(hold=True)
            title("compressed graph")

            show()


        """
        if node not in self.nodes():
            msg = "node %s is not in the graph" % node
            raise ValueError(msg)

        # there is always a MIDAS file for now but we may remove it later on
        specialNodes = self.inhibitors + self.signals  + self.stimuli
        notcompressable = [x for x in self.nodes() if x in specialNodes]
        if node in notcompressable:
            return False

        succs = self.successors(node)
        preds = self.predecessors(node)

        # if one input is an input, no compression
        if len(set(succs).intersection(set(preds))) > 0:
            self.logging.debug('skipped node (retroaction ? %s) ' % node)
            #print("%s case cycle input is in output" % node)
            return False

        # if no output or no input, can be compressed.
        # somehow this is redundant with NONC algorithm, which is not required
        # anymore.
        if len(self.successors(node)) == 0 or len(self.predecessors(node))==0:
            self.logging.debug('skipped node %s (input/output case ' % node)
            return True

        # if multiple input AND multiple output, no ambiguity: nothing to compress
        elif len(self.successors(node)) >1 and len(self.predecessors(node))>1:
            self.logging.debug('skipped node %s >1,>1 case ' % node)
            return False

        # if one input and several outputs OR several input and one ouptut, we
        # can compress. However, if the compressable node once removed is an
        # edge that already exists, then we will have multiedges, which is not
        # handled in a DIgraph. So, we cannot comrpess that particular case.


        # if one input only and one output only, no ambiguity: we can compress
        elif len(self.predecessors(node)) == 1 and len(self.successors(node))==1:
            ambiguous = self._ambiguous_multiedge(node)
            if ambiguous == True:
                self.logging.debug('%s could be compressed but ambiguity with existing edge so not removed ' % node)
                return False
            else:
                self.logging.debug('Add node %s =1,=1 to be removed ' % node)
                return True

        # one output but several input may be ambiguous. If output is inhibitor
        # and input contains an mix of inhibitor/activation then we can not
        # compress
        elif len(preds) > 1 and len(succs)==1:
            input_links = [self[p][node]['link'] for p in preds]
            output_links = self[node][succs[0]]['link']
            if (output_links == "-") and len(set(input_links))>=2:
                self.logging.debug('skipped node %s output=inhibitor and ambiguous inputs' % node)
                return False
            else:
                ambiguous = self._ambiguous_multiedge(node)
                if ambiguous == True:
                    self.logging.debug('%s could be compressed but ambiguity with existing edge so not removed ' % node)
                    return False
                else:
                    self.logging.debug('Add node %s >1,=1 case to be removed' % node)
                    return True

        # one input and several ouptut, no ambiguity: we can compress
        elif len(preds) == 1 and len(succs)>1:
            ambiguous = self._ambiguous_multiedge(node)
            if ambiguous == True:
                self.logging.debug('%s could be compressed but ambiguity with existing edge so not removed ' % node)
                return False
            else:
                self.logging.debug('Add node %s =1,>1 case to be removed' % node)
                return True
        else:
            self.logging.debug('do not remove node %s' % node)
            return False

    def relabel_nodes(self, mapping):
        """see :meth:`rename_node`

        """
        return self.rename_node(mapping)

    def rename_node(self, mapping):
        """Function to rename a node, while keeping all its attributes.


        :param dict mapping: a dictionary mapping old names (keys) to new names
            (values )
        :return: new cnograph object


        if we take this example::

            c = CNOGraph();
            c.add_reaction("a=b");
            c.add_reaction("a=c");
            c.add_reaction("b=d");
            c.add_reaction("c=d");
            c.expand_and_gates()

        Here, an AND gate has been created. c.nodes() tells us that its name is
        "b^c=d". If we rename the node b to blong, the AND gate name is
        unchanged if we use the nx.relabel_nodes function. Visually, it is
        correct but internally, the "b^c=d" has no more meaning since the node
        "b" does not exist anymore. This may lead to further issues if we for
        instance split the node c::

            c = nx.relabel_nodes(c, {"b": "blong"})
            c.split_node("c", ["c1", "c2"])

        This function calls relabel_node taking care of the AND nodes as well.

        .. warning:: this is not inplace modifications.

        .. todo:: midas must also be modified

        """

        for this in self._find_and_nodes():
            reac = Reaction(this)
            reac.rename_species(mapping)
            # add to mapping
            if reac.name != this:
                mapping.update({this:reac.name})

        c = nx.relabel_nodes(self, mapping)
        c._stimuli = self._stimuli[:]
        c._inhibitors = self._inhibitors[:]
        c._signals = self._signals[:]
        c._compressed = self._compressed[:]

        for old, new in mapping.iteritems():
            if old in c._stimuli:
                c._stimuli.append(new)
                c._stimuli.remove(old)
            if old in c._signals:
                c._signals.append(new)
                c._signals.remove(old)
            if old in c._inhibitors:
                c._inhibitors.append(new)
                c._inhibitors.remove(old)
        # TODO: rename midas as well !
        try:
            c.midas = self.midas.copy()
        except:
            pass

        return c
        # need to copt with the and reactions if any

    def centrality_eigenvector(self, max_iter=1000, tol=0.1):
        res = nx.eigenvector_centrality(self,max_iter,tol=tol)
        nx.set_node_attributes(self, 'eigenvector', res)
        nx.set_node_attributes(self, 'centrality_eigenvector', res)
        import operator
        degcent_sorted = sorted(res.items(), key=operator.itemgetter(1), reverse=True)
        #for k,v in degcent_sorted:
        #    self.logging.info("Highest degree centrality %s %s", v,k)
        return res

    def centrality_degree(self):
        """Compute the degree centrality for nodes.

        The degree centrality for a node v is the fraction of nodes it
        is connected to.

        :return: list of nodes with their degree centrality. It is also added to the list
            of attributes with the name "degree_centr"

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph, cnodata
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.centrality_degree()
            c.plot(node_attribute="centrality_degree")


        """
        res = nx.degree_centrality(self)
        nx.set_node_attributes(self, 'degree', res)
        nx.set_node_attributes(self, 'centrality_degree', res)
        import operator
        degcent_sorted = sorted(res.items(), key=operator.itemgetter(1), reverse=True)
        #for k,v in degcent_sorted:
        #    self.logging.info("Highest degree centrality %s %s", v,k)
        return res

    def centrality_closeness(self, **kargs):
        """Compute closeness centrality for nodes.

        Closeness centrality at a node is 1/average distance to all other nodes.

        :param v: node, optional  Return only the value for node v
        :param str distance: string key, optional (default=None)  Use specified edge key as edge distance.   If True, use 'weight' as the edge key.
        :param bool normalized:  optional   If True (default) normalize by the graph size.

        :return: Dictionary of nodes with closeness centrality as the value.

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph, cnodata
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.centrality_closeness()
            c.plot(node_attribute="centrality_closeness")

        """
        res = nx.centrality.closeness_centrality(self, **kargs)

        nx.set_node_attributes(self, 'closeness', res)
        nx.set_node_attributes(self, 'centrality_closeness', res)
        import operator
        degcent_sorted = sorted(res.items(), key=operator.itemgetter(1), reverse=True)
        #for k,v in degcent_sorted:
        #    self.logging.info("Highest closeness centrality %s %s", v,k)
        return res

    def centrality_betweeness(self, k=None, normalized=True,
        weight=None, endpoints=False, seed=None):
        r"""Compute the shortest-path betweeness centrality for nodes.

        Betweenness centrality of a node `v` is the sum of the
        fraction of all-pairs shortest paths that pass through `v`:

        .. math::

            c_B(v) =\sum_{s,t \in V} \frac{\sigma(s, t|v)}{\sigma(s, t)}

        where :math:`V` is the set of nodes, :math:`\sigma(s, t)` is the number of
        shortest :math:`(s, t)`-paths,  and :math:`\sigma(s, t|v)` is the number of those
        paths  passing through some  node :math:`v` other than :math:`s, t`.
        If :math:`s = t`, :math:`\sigma(s, t) = 1`, and if :math:`v \in {s, t}`,
        :math:`\sigma(s, t|v) = 0` .

        :param int k: (default=None)
          If k is not None use k node samples to estimate betweeness.
          The value of k <= n where n is the number of nodes in the graph.
          Higher values give better approximation.
        :param bool normalized:   If True the betweeness values are normalized by :math:`2/((n-1)(n-2))`
          for graphs, and :math:`1/((n-1)(n-2))` for directed graphs where :math:`n`
          is the number of nodes in G.
        :param str weight: None or string, optional
          If None, all edge weights are considered equal.

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph, cnodata
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.centrality_betweeness()
            c.plot(node_attribute="centrality_betweeness")

        .. seealso:: networkx.centrality.centrality_betweeness

        """
        res = nx.centrality.betweenness_centrality(self,k=k,normalized=normalized,
            weight=weight, endpoints=endpoints, seed=seed)
        nx.set_node_attributes(self, 'centrality_betweeness', res)
        nx.set_node_attributes(self, 'betweeness', res)
        import operator
        degcent_sorted = sorted(res.items(), key=operator.itemgetter(1), reverse=True)
        #for k,v in degcent_sorted:
        #    self.logging.info("Highest betweeness centrality %s %s", v,k)
        return res

    def export2gexf(self, filename):
        """Export into GEXF format

        :param str filename:

        This is the networkx implementation and requires the version 1.7
        This format is quite rich and can be used in external software such as Gephi.

        .. warning:: color and labels are lost. information is stored as
            attributes.and should be as properties somehow.
            Examples:  c.node['mkk7']['viz'] =  {'color': {'a': 0.6, 'r': 239, 'b': 66,'g': 173}}

        """
        from networkx.readwrite import write_gexf
        write_gexf(self, filename)

    def to_directed(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def to_sif(self, filename=None):
        """Export CNOGraph into a SIF file.

        Takes into account and gates. If a species called  "A^B=C" is found, it is an AND
        gate that is encoded in a CSV file as::

            A 1 and1
            B 1 and1
            and1 1 C

        :param str filename:

        """
        sif = SIF()

        for edge in self.edges(data=True):
            n1 = edge[0]
            n2 = edge[1]
            link = edge[2]['link']
            reaction = ""
            if self.isand(n1) is False and self.isand(n2) is False:
                if link == "-":
                    reaction += "!"
                reaction += n1 + "=" + n2
                sif.add_reaction(reaction)
        for edge in self._find_and_nodes():
            sif.add_reaction(edge)

        if filename:
            sif.save(filename)
        else:
            return sif

    def to_json(self, filename=None):
        """Export the graph into a JSON format

        :param str filename:

        .. seealso:: :meth:`loadjson`
        """
        from networkx.readwrite import json_graph
        data = json_graph.node_link_data(self)
        if filename is not None:
            json.dump(data, open(filename, "w"))
        else:
            return data

    def read_sbmlqual(self, filename):
        sif = SIF()
        sif.read_sbmlqual(filename)
        self.clear()
        for reac in sif.reactions:
            self.add_reaction(reac)

    def to_sbmlqual(self, filename=None):
        """Export the topology into SBMLqual and save in a file

        :param str filename: if not provided, returns the SBML as a string.
        :return: nothing if filename is not provided

        .. seealso:: :meth:`cno.io.sbmlqual`
        """
        s = SIF()
        for reac in self.reactions:
            s.add_reaction(reac)
        return s.to_sbmlqual(filename=filename)

    def read_json(self, filename):
        """Load a network in JSON format as exported from :meth:`to_json`

        :param str filename:

        .. seealso:: :meth:`to_json`
        """
        from networkx.readwrite import json_graph
        graph = json_graph.load(open(filename))

        self.clear()

        for node in graph.nodes():
            self.add_node(node)
        for edge in graph.edges(data=True):
            self.add_edge(edge[0], edge[1], link=edge[2]['link'])

        return graph

    def lookfor(self, specyName):
        """Prints information about a species

        If not found, try to find species by ignoring cases.

        """
        #try to find the specy first:
        if specyName not in self.nodes():
            print("did not find the requested specy")
            proposals = [node for node in self.nodes() if specyName.lower() in node.lower()]
            if len(proposals):
                print("try one of ")
                for p in proposals:
                    print(proposals)
        else:
            print("predecessors")
            print(self.predecessors(specyName))
            print("successors")
            print(self.successors(specyName))

    def get_stats(self):
        stats = {}
        flow = nx.flow_hierarchy(self)
        stats['flow'] = flow
        stats['mean_degree'] = sum(self.degree().values())/float(len(self.nodes()))
        return stats

    def summary(self):
        """Plot information about the graph"""
        stats = self.get_stats()
        print("Flow hierarchy = %s (fraction of edges not participating in cycles)" % stats['flow'])
        print("Average degree = " + unicode(sum(self.degree().values())/float(len(self.nodes()))))

    def merge_nodes(self, nodes, node):
        """Merge several nodes into a single one

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            from pylab import subplot
            c = CNOGraph()
            c.add_edge("AKT2", "B", link="+")
            c.add_edge("AKT1", "B", link="+")
            c.add_edge("A", "AKT2", link="+")
            c.add_edge("A", "AKT1", link="+")
            c.add_edge("C", "AKT1", link="+")
            subplot(1,2,1)
            c.plot(hold=True)
            c.merge_nodes(["AKT1", "AKT2"], "AKT")
            subplot(1,2,2)
            c.plot(hold=True)


        """
        assert len(nodes)>1, "nodes must be a list of species"
        for n in nodes:
            if n not in self.nodes():
                raise ValueError("%s not found in the graph !" % n)

        self.add_node(node)
        for n in nodes:
            for pred in self.predecessors(n):
                attrs = self.edge[pred][n]
                if self.isand(pred):
                    pred = self._rename_node_in_reaction(pred, n, node)
                    self.add_reaction(pred)
                else:
                    self.add_edge(pred, node, **attrs)
            for succ in self.successors(n):
                attrs = self.edge[n][succ]
                if self.isand(succ):
                    succ = self._rename_node_in_reaction(succ, n, node)
                    self.add_reaction(succ)
                else:
                    self.add_edge(node, succ, **attrs)
        for n in nodes:
            self.remove_node(n)

        # assume that all nodes are in signals if first one is in signal.
        # FIXME: not robust
        if nodes[0] in self._signals:
            for this in nodes:
                self._signals.remove(this)
            self._signals.append(node)
        if nodes[0] in self._stimuli:
            for this in nodes:
                self._stimuli.remove(this)
            self._stimuli.append(node)
        if nodes[0] in self._inhibitors:
            for this in nodes:
                self._inhibitors.remove(this)
            self._inhibitors.append(node)

    def split_node(self, node, nodes):
        """

        .. plot::
            :include-source:
            :width: 50%

            from cno import CNOGraph
            from pylab import subplot
            c = CNOGraph()
            c.add_reaction("!A=C")
            c.add_reaction("B=C")
            c.add_reaction("!b1=B")
            c.add_reaction("b2=B")
            c.expand_and_gates()

            subplot(1,2,1)
            c.plot(hold=True)

            c.split_node("B", ["B1", "B2", "B3"])
            subplot(1,2,2)
            c.plot(hold=True)

       """
        for n in nodes:
            for pred in self.predecessors(node):
                attrs = self.edge[pred][node]
                if self.isand(pred):
                    pred = self._rename_node_in_reaction(pred, node, n)
                    self.add_reaction(pred)
                else:
                    self.add_edge(pred, n, **attrs)

            for succ in self.successors(node):
                attrs = self.edge[node][succ]
                # special case of the AND gates
                if self.isand(succ):
                    succ = self._rename_node_in_reaction(succ, node, n)
                    self.add_reaction(succ)
                else: # normal case
                    self.add_edge(n, succ, **attrs)
        self.remove_node(node)
        # remove AND gates as well:
        for this in self._find_and_nodes():
            gate = Reaction(this)
            if node in gate.lhs_species:
                self.remove_node(this)

        if node in self._signals:
            self._signals.extend(nodes)
            self._signals.remove(node)
        if node in self._stimuli:
            self._stimuli.extend(nodes)
            self._stimuli.remove(node)
        if node in self._inhibitors:
            self._inhibitors.extend(nodes)
            self._inhibitors.remove(node)

    def _rename_node_in_reaction(self, reaction, old, new):
        """This function rename a species within a reaction."""
        reac = Reaction(reaction)
        reac.rename_species({old:new})
        return reac.name

    def findnonc(self):
        """Finds the Non-Observable and Non-Controllable nodes

        #. Non observable nodes are those that do not have a path to any measured
           species in the PKN
        #. Non controllable nodes are those that do not receive any information
           from a species that is perturbed in the data.

        Such nodes can be removed without affecting the readouts.


        :param G: a CNOGraph object
        :param stimuli: list of stimuli
        :param stimuli: list of signals

        :return: a list of names found in G that are NONC nodes

        .. doctest::

            >>> from cno import CNOGraph, cnodata
            >>> model = cnodata('PKN-ToyMMB.sif')
            >>> data = cnodata('MD-ToyMMB.csv')
            >>> c = CNOGraph(model, data)
            >>> namesNONC = c.nonc()

        :Details: Using a floyd Warshall algorithm to compute path between nodes in a
          directed graph, this class
          identifies the nodes that are not connected to any signals (Non Observable)
          and/or any stimuli (Non Controllable) excluding the signals and stimuli,
          which are kept whatever is the outcome of the FW algorithm.
        """
        # some aliases
        assert (self.stimuli!=None and self.signals!=None)

        dist = nx.algorithms.floyd_warshall(self)

        namesNONC = []
        for node in self.nodes():
            # search for paths from the species to the signals
            spe2sig = [(node, dist[node][s]) for s in self.signals if dist[node][s]!=np.inf]
            # and from the nstimuli to the species
            sti2spe = [(node, dist[s][node]) for s in self.stimuli if dist[s][node]!=np.inf]

            if len(spe2sig)==0 or len(sti2spe)==0:
                if node not in self.signals and node not in self.stimuli:
                    namesNONC.append(node)

        namesNONC  = list(set(namesNONC)) # required ?
        return namesNONC

    def random_poisson_graph(self, n=10, mu=3, remove_unconnected=False):
        from scipy.stats import poisson
        z = [poisson.rvs(mu) for i in range(0,n)]
        G = nx.expected_degree_graph(z)
        self.clear()
        # converts to strings
        self.add_edges_from(G.edges(), link="+")
        if remove_unconnected==False:
            self.add_nodes_from(G.nodes())

        ranks = self.get_same_rank()
        sources = ranks[0]
        sinks = ranks[max(ranks.keys())]
        self._stimuli = sources[0::2]
        self._signals = sinks[0::2]


    def remove_self_loops(self):
        for e in self.edges():
            if e[0] == e[1]:
                self.remove_edge(e[0], e[1])



