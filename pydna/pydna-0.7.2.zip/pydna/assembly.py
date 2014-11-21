#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''This module provides functions for assembly of sequences by homologous recombination and other
related techniques. Given a list of sequences (Dseqrecords), all sequences will be analyzed for
overlapping regions of DNA (common substrings).

The assembly algorithm is based on graph theory where each overlapping region forms a node and
sequences separating the overlapping regions form edges.

'''

import itertools
import networkx as nx
import operator
import random

from copy import copy
from textwrap import dedent
from collections import defaultdict

from Bio.SeqFeature import FeatureLocation
from Bio.SeqFeature import SeqFeature

from pydna.dsdna import Dseq
from pydna.dsdna import Dseqrecord
from pydna._simple_paths8 import all_simple_paths_edges, all_circular_paths_edges
from findsubstrings_suffix_arrays_python import common_sub_strings
from findsubstrings_suffix_arrays_python import terminal_overlap

from orderedset import OrderedSet

class Fragment(Dseqrecord):
    '''This class holds information about a DNA fragment in an assembly.
    This class is instantiated by the :class:`Assembly` class and is not
    meant to be instantiated directly.

    '''

    def __init__(self, record, start1    = 0,
                               end1      = 0,
                               start2    = 0,
                               end2      = 0,
                               alignment = 0,
                               i         = 0, *args, **kwargs):

        super(Fragment, self).__init__(record, *args, **kwargs)

        self.start1             = start1
        self.end1               = end1
        self.left_overlap_size  = end1-start1
        self.start2             = start2
        self.end2               = end2
        self.right_overlap_size = end2-start2
        self.alignment          = alignment
        self.i                  = i

    def __str__(self):
        return ("Fragment alignment {}\n").format(self.alignment)+super(Fragment, self).__str__()

class Contig(Dseqrecord):
    '''This class holds information about a DNA assembly. This class is instantiated by
    the :class:`Assembly` class and is not meant to be instantiated directly.

    '''

    def __init__(self,
                 record,
                 source_fragments=[],
                 *args, **kwargs):

        super(Contig, self).__init__(record, *args, **kwargs)
        self.source_fragments = source_fragments
        self.number_of_fragments = len(self.source_fragments)

    def detailed_figure(self):
        '''Synonym of :func:`detailed_fig`'''
        return self.detailed_fig()

    def detailed_fig(self):

        fig=""
        for s in self.source_fragments:
            fig +="{}{}\n".format(" "*s.alignment, str(s.seq))
        return fig

    def small_figure(self):
        '''Synonym of :func:`small_fig`'''
        return self.small_fig()

    def small_fig(self):
        '''
        Returns a small ascii representation of the assembled fragments. Each fragment is
        represented by:

        ::

         Size of common 5' substring|Name and size of DNA fragment| Size of common 5' substring

        Linear:

        ::

          frag20| 6
                 \\/
                 /\\
                  6|frag23| 6
                           \\/
                           /\\
                            6|frag14


        Circular:

        ::

          -|2577|61
         |       \\/
         |       /\\
         |       61|5681|98
         |               \\/
         |               /\\
         |               98|2389|557
         |                       \\/
         |                       /\\
         |                       557-
         |                          |
          --------------------------


        '''

        if self.linear:
            '''
            frag20| 6
                   \/
                   /\
                    6|frag23| 6
                             \/
                             /\
                              6|frag14
            '''
            f = self.source_fragments[0]
            space2 = len(f.name)


            fig = ("{name}|{o2:>2}\n"
                   "{space2} \/\n"
                   "{space2} /\\\n").format(name = f.name,
                                            o2 = f.right_overlap_size,
                                            space2 = " "*space2)
            space = len(f.name)

            for f in self.source_fragments[1:-1]:
                name= "{o1:>2}|{name}|".format(o1   = f.left_overlap_size,
                                               name = f.name)
                space2 = len(name)
                fig +=("{space} {name}{o2:>2}\n"
                       "{space} {space2}\/\n"
                       "{space} {space2}/\\\n").format( name = name,
                                                        o2 = f.right_overlap_size,
                                                        space = " "*space,
                                                        space2 = " "*space2)
                space +=space2
            f = self.source_fragments[-1]
            fig += ("{space} {o1:>2}|{name}").format(name = f.name,
                                                    o1 = f.left_overlap_size,
                                                    space = " "*(space))



        else:
            '''
             -|2577|61
            |       \/
            |       /\
            |       61|5681|98
            |               \/
            |               /\
            |               98|2389|557
            |                       \/
            |                       /\
            |                       557-
            |                          |
             --------------------------
            '''
            f = self.source_fragments[0]
            space = len(f.name)+3
            fig =(" -|{name}|{o2:>2}\n"
                  "|{space}\/\n"
                  "|{space}/\\\n").format(name = f.name,
                                           o2 = f.right_overlap_size,
                                           space = " "*space)
            for f in self.source_fragments[1:]:
                name= "{o1:>2}|{name}|".format(o1 = f.left_overlap_size,
                                                      name = f.name)
                space2 = len(name)
                fig +=("|{space}{name}{o2:>2}\n"
                       "|{space}{space2}\/\n"
                       "|{space}{space2}/\\\n").format(o2 = f.right_overlap_size,
                                                       name = name,
                                                       space = " "*space,
                                                       space2 = " "*space2)
                space +=space2

            fig +="|{space}{o1:>2}-\n".format(space=" "*(space), o1=self.source_fragments[0].left_overlap_size)
            fig +="|{space}   |\n".format(space=" "*(space))
            fig +=" {space}".format(space="-"*(space+3))
        return dedent(fig)

class Assembly(object):
    '''Assembly of a list of linear DNA fragments into linear or circular constructs.
    Accepts a list of Dseqrecords (source fragments) to initiate an Assembly object.
    Several methods are available for analysis of overlapping sequences, graph construction
    and assembly.

    Parameters
    ----------

    dsrecs : list
        a list of Dseqrecord objects.

    Examples
    --------

    >>> from pydna import Assembly, Dseqrecord
    >>> a = Dseqrecord("acgatgctatactgCCCCCtgtgctgtgctcta")
    >>> b = Dseqrecord("tgtgctgtgctctaTTTTTtattctggctgtatc")
    >>> c = Dseqrecord("tattctggctgtatcGGGGGtacgatgctatactg")
    >>> x = Assembly((a,b,c), limit=14)
    >>> x.analyze_overlaps()
    '6 sequences analyzed of which 3 have shared homologies with totally 3 overlaps'
    >>> x.create_graph()
    "A graph with 5', 3' and 3 internal nodes was created"
    >>> x.assemble_circular_from_graph()
    '1 circular products were formed'
    >>> x
    Assembly object:
    Sequences........................: 33, 34, 35
    Sequences with shared homologies.: 33, 34, 35
    Homology limit (bp)..............: 14
    Number of overlaps...............: 3
    Nodes in graph...................: 5
    Assembly protocol................: overlaps
    Circular products................: 59
    Linear products..................: No linear products
    >>> x.circular_products
    [Dseqrecord(o59)]
    >>> x.circular_products[0].seq.watson
    'CCCCCtgtgctgtgctctaTTTTTtattctggctgtatcGGGGGtacgatgctatactg'


    '''

    def __init__(self, dsrecs, limit = 25):
        self.dsrecs    = dsrecs
        ''' Sequences fed to this class is stored in this property'''
        self.max_nodes = len(self.dsrecs)
        ''' The max number of nodes allowed. This can be reset to some other value'''
        self.limit     = limit
        ''' The shortest common sub strings to be considered '''

        for dr in self.dsrecs:
            if dr.name in ("",".", "<unknown name>", None):
                dr.name = "frag{}".format(len(dr))

    def analyze_overlaps(self, limit=None):
        '''This method carries out a pairwise analysis for common sub strings (shared homologous sequences)
        among DNA fragments stored in the dsrecs property.

        * Common sub strings need to be equal to or longer than limit.
        * Common sub strings can be present anywhere within the sequences stored in the dsrecs property.

        The analyzed_dsrec property will contain copies of the sequences in the dsrecs property that have
        common substrings. Common sub strings are added as features to the sequences in the analyzed_dsrec
        property.



        Parameters
        ----------

        limit : int
            The shortest shared sub sequence to be considered. This will also set the limit property.

        See also
        --------
        pydna.assembly.Assembly.analyze_terminal_overlaps

        '''

        if limit:
            self.limit = limit
        self.protocol = "overlaps"
        return self._analyze_overlaps(common_sub_strings)

    def analyze_terminal_overlaps(self, limit=None):
        '''This method carries out a pairwise analysis for shared sub sequences equal to or longer than
        limit. The difference between this method and :func:`analyze_overlaps` is that shared sequences
        must start or end at the extremities of the source fragments.

        Parameters
        ----------

        limit : int
            The shortest shared sub sequence to be considered. This will also set the limit property.

        See also
        --------
        pydna.assembly.Assembly.analyze_overlaps

        '''
        if limit:
            self.limit = limit
        self.protocol = "terminal overlaps"
        return self._analyze_overlaps(terminal_overlap)

    def create_graph(self):
        '''Creates a graph from analyzed source fragments. Nodes in the graph are shared sub sequences
        found as features in the source sequences. Edges are the sequences that connect the shared
        sub sequences in each source fragment. Two additional nodes called 5' and 3' are also added to
        represent DNA ends.
        '''
        return self._create_graph()

    def assemble_circular_from_graph(self):
        '''Assembles all circular products from the graph created by :func:`create_graph`'''
        self.circular_products = self._circ()
        return "{} circular products were formed".format(len(self.circular_products))

    def assemble_linear_from_graph(self):
        '''Assembles all linear products from the graph created by :func:`create_graph`'''
        self.linear_products = self._lin()
        return "{} linear products were formed".format(len(self.linear_products))

    def assemble_hr_circular(self, limit=None):
        '''Convenience method to assembles all possible circular homologous recombination (hr) products
        expected from in-vivo homologous recombination by the following steps:

        1. Analysis of source fragments using the :func:`analyze_overlaps` method
        2. Construction of a graph using the :func:`create_graph` method
        3. Assembly of possible circular products using the :func:`assemble_circular_from_graph` method

        The property "circular_products" is initiated with a list of :class:`Fragment` objects.

        '''
        if limit:
            self.limit = limit
        self.analyze_overlaps()
        self.create_graph()
        self.assemble_circular_from_graph()
        self.protocol = "homologous recombination, circular"
        return "{} circular products were formed".format(len(self.circular_products))

    def assemble_hr_linear(self, limit = None):
        '''Convenience method to assembles all possible linear homologous recombination (hr) products
        expected from in-vivo homologous recombination by the following steps:

        1. Analysis of source fragments using the :func:`analyze_overlaps` method
        2. Construction of a graph using the :func:`create_graph` method
        3. Assembly of possible linear products using the :func:`assemble_linear_from_graph` method

        The property "linear_products" is initiated with a list of :class:`Fragment` objects.

        '''
        if limit:
            self.limit = limit
        self.analyze_overlaps()
        self._create_graph()
        self.linear_products = self._lin()
        self.protocol = "homologous recombination, linear"
        return "{} linear products were formed".format(len(self.linear_products))

    def assemble_gibson_circular(self, limit = None):
        '''Convenience method to assembles all possible circular Gibson assembly products
        expected from in-vivo homologous recombination by the following steps:

        1. Analysis of source fragments using the :func:`analyze_terminal_overlaps` method
        2. Construction of a graph using the :func:`create_graph` method
        3. Assembly of possible circular products using the :func:`assemble_circular_from_graph` method

        The property "circular_products" is initiated with a list of :class:`Fragment` objects.

        '''
        if limit:
            self.limit = limit
        self.analyze_terminal_overlaps()
        self._create_graph()
        self.circular_products = self._circ()
        self.protocol = "gibson assembly, circular"
        return "{} circular products were formed with the following sizes (bp): {}".format(len(self.circular_products),
                                                                                           ", ".join(str(len(x)) for x in self.circular_products))

    def assemble_gibson_linear(self, limit = None):
        '''Convenience method to assembles all possible linear Gibson assembly products
        expected from in-vivo homologous recombination by the following steps:

        1. Analysis of source fragments using the :func:`analyze_terminal_overlaps` method
        2. Construction of a graph using the :func:`create_graph` method
        3. Assembly of possible circular products using the :func:`assemble_linear_from_graph` method

        The property "linear_products" is initiated with a list of :class:`Fragment` objects.

        '''
        if limit:
            self.limit = limit
        self.analyze_terminal_overlaps()
        self._create_graph()
        self.linear_products = self._lin()
        self.protocol = "gibson assembly, linear"
        return "{} linear products were formed with the following sizes (bp): {}".format( len(self.linear_products),
                                                                                          ", ".join(str(len(x)) for x in self.linear_products))
    def assemble_fusion_pcr_linear(self, limit = None):
        '''Convenience method to assembles all possible linear fusion PCR products.
        This method is a synonym of :func:`assemble_gibson_linear`
        '''
        self.assemble_gibson_linear(limit)
        self.protocol = "fusion PCR, linear"
        return "{} linear products were formed".format(len(self.linear_products))

    def assemble_slic(self, limit = None):
        '''Not implemented'''
        self.protocol = "slic, linear"
        raise NotImplementedError

    def assemble_golden_gate(self, limit = None):
        '''Not implemented'''
        self.protocol = "golden_gate"
        raise NotImplementedError

    def _create_graph(self):

        self.G=nx.MultiDiGraph(multiedges=True, name ="original graph" , selfloops=False)
        self.G.add_node( '5' )
        self.G.add_node( '3' )

        for i, dsrec in enumerate(self.analyzed_dsrecs):

            overlaps = sorted( {f.qualifiers['chksum'][0]:f for f in dsrec.features
                                if f.type=='overlap'}.values(),
                               key = operator.attrgetter('location.start'))

            if overlaps:
                overlaps = ([SeqFeature(FeatureLocation(0, 0),
                             type = 'overlap',
                             qualifiers = {'chksum':['5']})]+
                             overlaps+
                            [SeqFeature(FeatureLocation(len(dsrec),len(dsrec)),
                                        type = 'overlap',
                                        qualifiers = {'chksum':['3']})])

                for olp1, olp2 in itertools.combinations(overlaps, 2):

                    n1 = olp1.qualifiers['chksum'][0]
                    n2 = olp2.qualifiers['chksum'][0]

                    if n1 == '5' and n2=='3':
                        continue

                    s1,e1,s2,e2 = (olp1.location.start.position,
                                   olp1.location.end.position,
                                   olp2.location.start.position,
                                   olp2.location.end.position,)

                    source_fragment = Fragment(dsrec,s1,e1,s2,e2,i)

                    self.G.add_edge( n1, n2,
                                     frag=source_fragment,
                                     weight = s1-e1,
                                     i = i)
        return '''A graph with 5', 3' and {nodes} internal nodes was created'''.format(nodes = self.G.order()-2)


    def _analyze_overlaps(self, algorithm):
        cols = {}
        for dsrec in self.dsrecs:
            dsrec.features = [f for f in dsrec.features if f.type!="overlap"]
            dsrec.seq = Dseq(dsrec.seq.todata)
        rcs = {dsrec:dsrec.rc() for dsrec in self.dsrecs}
        matches=[]
        dsset=OrderedSet()

        for a, b in itertools.combinations(self.dsrecs, 2):
            #print len(a),len(b)
            #a,b = b,a
            match = algorithm( str(a.seq).upper(),
                               str(b.seq).upper(),
                               self.limit)
            if match:
                matches.append((a, b, match))
                dsset.add(a)
                dsset.add(b)
            match = algorithm( str(a.seq).upper(),
                               str(rcs[b].seq).upper(),
                               self.limit)
            if match:
                matches.append((a, rcs[b], match))
                dsset.add(a)
                dsset.add(rcs[b])
                matches.append((rcs[a], b, [(len(a)-sa-le,len(b)-sb-le,le) for sa,sb,le in match]))
                dsset.add(b)
                dsset.add(rcs[a])

        self.no_of_olaps=0

        for a, b, match in matches:
            for start_in_a, start_in_b, length in match:
                self.no_of_olaps+=1
                chksum = a[start_in_a:start_in_a+length].seguid()
                assert chksum == b[start_in_b:start_in_b+length].seguid()

                try:
                    fcol, revcol = cols[chksum]
                except KeyError:
                    fcol = '#%02X%02X%02X' % (random.randint(175,255),random.randint(175,255),random.randint(175,255))
                    rcol = '#%02X%02X%02X' % (random.randint(175,255),random.randint(175,255),random.randint(175,255))
                    cols[chksum] = fcol,rcol

                qual      = {"note"             : ["olp_{}".format(chksum)],
                             "chksum"           : [chksum],
                             "ApEinfo_fwdcolor" : [fcol],
                             "ApEinfo_revcolor" : [rcol]}

                if not chksum in [f.qualifiers["chksum"][0] for f in a.features if f.type == "overlap"]:
                    a.features.append( SeqFeature( FeatureLocation(start_in_a,
                                                                   start_in_a + length),
                                                                   type = "overlap",
                                                                   qualifiers = qual))
                if not chksum in [f.qualifiers["chksum"][0] for f in b.features if f.type == "overlap"]:
                    b.features.append( SeqFeature( FeatureLocation(start_in_b,
                                                                   start_in_b + length),
                                                                   type = "overlap",
                                                                   qualifiers = qual))
        for ds in dsset:
            ds.features = sorted([f for f in ds.features], key = operator.attrgetter("location.start"))

        self.analyzed_dsrecs = list(dsset)

        return ( "{number_of_seqs} sequences analyzed "
                 "of which {analyzed_dsrecs} have shared homologies "
                 "with totally {no_of_olaps} overlaps").format(number_of_seqs  = len(self.dsrecs)*2,
                                                               analyzed_dsrecs = len(self.analyzed_dsrecs),
                                                               no_of_olaps     = self.no_of_olaps)


    def _circ(self):
        self.cG = self.G.copy()
        self.cG.remove_nodes_from(('5','3'))
        circular_products=defaultdict(list)

        for pth in all_circular_paths_edges(self.cG):

            ns = min(enumerate(pth), key = lambda x:x[1][2]['i'])[0]

            path = pth[ns:]+pth[:ns]

            pred_frag = copy(path[0][2]['frag'])

            source_fragments = [pred_frag, ]

            if pred_frag.start2<pred_frag.end1:
                result=pred_frag[pred_frag.start2+(pred_frag.end1-pred_frag.start2):pred_frag.end2]
            else:
                result=pred_frag[pred_frag.end1:pred_frag.end2]

            result.seq = Dseq(str(result.seq))

            for first_node, second_node, edgedict in path[1:]:

                f  = copy(edgedict['frag'])

                f.alignment =  pred_frag.alignment + pred_frag.start2- f.start1
                source_fragments.append(f)

                if f.start2>f.end1:
                    nxt = f[f.end1:f.end2]
                else:
                    nxt =f[f.start2+(f.end1-f.start2):f.end2]
                nxt.seq = Dseq(str(nxt.seq))
                result+=nxt

                pred_frag = f

            add=True
            for cp in circular_products[len(result)]:
                if (str(result.seq).lower() in str(cp.seq).lower()*2
                    or
                    str(result.seq).lower() == str(cp.seq.reverse_complement()).lower()*2):
                    pass
                    add=False
            if add:
                circular_products[len(result)].append( Contig( Dseqrecord(result, circular=True), source_fragments))

        return list(itertools.chain.from_iterable(circular_products[size] for size in sorted(circular_products, reverse=True)))


    def _lin(self):

        linear_products=defaultdict(list)

        for path in all_simple_paths_edges(self.G, '5', '3', data=True, cutoff=self.max_nodes):

            pred_frag = copy(path[0][2].values().pop()['frag'])
            source_fragments = [pred_frag, ]

            if pred_frag.start2<pred_frag.end1:
                result=pred_frag[pred_frag.start2+(pred_frag.end1-pred_frag.start2):pred_frag.end2]
            else:
                result=pred_frag[pred_frag.end1:pred_frag.end2]

            for first_node, second_node, edgedict in path[1:]:

                edgedict = edgedict.values().pop()

                f  = copy(edgedict['frag'])

                f.alignment =  pred_frag.alignment + pred_frag.start2- f.start1
                source_fragments.append(f)

                if f.start2>f.end1:
                    result+=f[f.end1:f.end2]
                else:
                    result+=f[f.start2+(f.end1-f.start2):f.end2]

                pred_frag = f

            add=True
            for lp in linear_products[len(result)]:
                if (str(result.seq).lower() == str(lp.seq).lower()
                    or
                    str(result.seq).lower() == str(lp.seq.reverse_complement()).lower()):
                    add=False
            for dsrec in self.dsrecs:
                if (str(result.seq).lower() == str(dsrec.seq).lower()
                    or
                    str(result.seq).lower() == str(dsrec.seq.reverse_complement()).lower()):
                    add=False
            if add:
                linear_products[len(result)].append(Contig( result, source_fragments))

        return list(itertools.chain.from_iterable(linear_products[size] for size in sorted(linear_products, reverse=True)))

    def __repr__(self):

        try:
            number_of_seqs  =  ", ".join(str(len(x)) for x in self.dsrecs)
        except AttributeError:
            number_of_seqs  =  "No sequences"
        try:
            analyzed_dsrecs = ", ".join(str(len(x)) for x in self.analyzed_dsrecs)
        except AttributeError:
            analyzed_dsrecs = "No analyzed sequences"
        try:
            limit = self.limit
        except AttributeError:
            limit = "No limit set"
        try:
            no_of_olaps = self.no_of_olaps
        except AttributeError:
            no_of_olaps = "No overlaps"
        try:
            nodes = self.G.order()
        except AttributeError:
            nodes = "No graph"
        try:
            pr = self.protocol
        except AttributeError:
            pr= "No protocol"
        try:
            cp = ", ".join(str(len(x)) for x in self.circular_products)
        except AttributeError:
            cp= "No circular products"
        try:
            lp = ", ".join(str(len(x)) for x in self.linear_products)
        except AttributeError:
            lp= "No linear products"

        return   ( "Assembly object:\n"
                   "Sequences........................: {number_of_seqs}\n"
                   "Sequences with shared homologies.: {analyzed_dsrecs}\n"
                   "Homology limit (bp)..............: {limit}\n"
                   "Number of overlaps...............: {no_of_olaps}\n"
                   "Nodes in graph...................: {nodes}\n"
                   "Assembly protocol................: {pr}\n"
                   "Circular products................: {cp}\n"
                   "Linear products..................: {lp}"    ).format(number_of_seqs  = number_of_seqs,
                                                                         analyzed_dsrecs = analyzed_dsrecs,
                                                                         limit           = limit,
                                                                         no_of_olaps     = no_of_olaps,
                                                                         nodes           = nodes,
                                                                         pr              = pr,
                                                                         cp              = cp,
                                                                         lp              = lp)

if __name__=="__main__":
    import doctest
    doctest.testmod()