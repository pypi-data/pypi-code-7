#!/usr/bin/env python

import re

from products import make_product
import networkx as nx

def parse_line(line):
    '''Parse one line from "ups depend".

    Return a tuple holding the depth of the line and a ProdDesc
    object.
    '''
    depth = 0
    if line.startswith('|'):
        m = re.match('([\| ]  )*\|__', line)
        if not m:
            raise ValueError, 'Failed to parse line: %s' % line
        pre = m.group(0)
        line = line[len(pre):]
        depth = len(pre)/3

    quals = ''
    chunks = line.split()
    if len(chunks) == 6:
        pkg,ver, f,flav, z,path = chunks
    elif len(chunks) == 8:    
        pkg,ver, f,flav, z,path, q,quals = chunks
    else:
        raise ValueError, 'parse failure for line: %s' % str(chunks)
    return depth, make_product(pkg, ver, quals, flav, path)

def parse(text):
    '''
    Parse text output from 'ups depend' and return it as a tree (DAG).

    Warning: https://github.com/brettviren/python-ups-utils/issues/1
    '''
    tree = nx.DiGraph()

    parents = list()
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        depth, pd = parse_line(line)

        tree.add_node(pd)
        if not parents:
            assert depth == 0
            parents.append(pd)
            continue

        parents = parents[:depth]
        parent = parents[-1]
        tree.add_edge(parent, pd)
        parents.append(pd)
        continue

    return tree



def full(uc, seeds):
    '''
    Create full dependency tree starting at given seeds.
    '''

    tree = nx.DiGraph()

    for pd in seeds:
        text = uc.depend(pd)
        ng = parse(text)
        tree.add_nodes_from(ng.nodes())
        tree.add_edges_from(ng.edges())

    seen = list(seeds)
    for pd in tree.nodes():
        if pd in seen:
            continue
        seen.append(pd)
        text = uc.depend(pd)
        ng = parse(text)
        tree.add_nodes_from(ng.nodes())
        tree.add_edges_from(ng.edges())
    # whew
    return tree

def roots(tree):
    '''
    Return sequence of nodes which have no parents.
    '''
    ret = set(tree.nodes())
    for edge in tree.edges():
        try:
            ret.remove(edge[1])
        except KeyError:
            pass
    return ret
