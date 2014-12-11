#!/usr/bin/env python
'''
Method for operating on the products tree
'''
import networkx as nx

#from .repos import UpsRepo
#from . import depend
#from ups.products import product_to_upsargs, upsargs_to_product, upslisting_to_product

import networkx as nx


def top_nodes(graph):
    top_nodes = set(graph.nodes())
    for edge in graph.edges():
        try:
            top_nodes.remove(edge[1])
        except KeyError:
            pass
    return top_nodes


def purge(graph, seeds):
    top = top_nodes(graph)

    dead = set(seeds)
    alive = top.difference(dead)

    dead_tree = nx.DiGraph()
    for n in dead:
        dead_tree.add_edges_from(nx.bfs_edges(graph, n))
    alive_tree = nx.DiGraph()
    for n in alive:
        alive_tree.add_edges_from(nx.bfs_edges(graph, n))

    return set(dead_tree.nodes()).difference(alive_tree.nodes())



# class Tree(object):
#     def __init__(self, commands):
#         self.uc = commands
#         self.repo = UpsRepo(self.uc.products_path)

#     def match(self, **kwds):
#         '''Return list of matching products.  

#         The <kwds> hold things to match on.  Keys should match
#         arguments of products.Product and values be regular
#         expressions (not globs).  Unknown keys are ignored.
#         '''
#         def match_one(pd):
#             for k,v in kwds.items():
#                 string = getattr(pd, k, None)
#                 if string is None:
#                     continue
#                 m = re.match(v, string)
#                 if not m:
#                     return
#                 g = m.group()
#                 if not g:
#                     return
#                 if g != m.string:
#                     return
#                 continue
#             return pd

#         ret = list()
#         for pd in self.available():
#             if match_one(pd):
#                 ret.append(pd)
#         return ret


#     def resolve(self, name ,version='', qualifiers='', flavor=''):
#         pd = self.repo.find_product(name, version, qualifiers, flavor or self.uc.flavor())
#         if not pd:
#             pd = self.repo.find_product(name, version, qualifiers, 'NULL')
#         return pd

#     def dependencies(self, seeds = None):
#         seeds = seeds or self.available()
#         return depend.full(self.uc, seeds)

#     def available(self):
#         availtext = self.uc.avail()
#         ret = set()
#         for line in availtext.split('\n'):
#             pd = upslisting_to_product(line)
#             ret.add(pd)

#         return ret

#     def top(self):
#         deps = self.dependencies()
#         return depend.roots(deps)
        
#     def purge(self, seeds):
#         full_tree = self.dependencies()
#         top = depend.roots(full_tree)

#         dead = set(seeds)
#         alive = top.difference(dead)

#         dead_tree = nx.DiGraph()
#         for n in dead:
#             dead_tree.add_edges_from(nx.bfs_edges(full_tree, n))
#         alive_tree = nx.DiGraph()
#         for n in alive:
#             alive_tree.add_edges_from(nx.bfs_edges(full_tree, n))

#         return set(dead_tree.nodes()).difference(alive_tree.nodes())

