#!/usr/bin/env python
'''
Make Graphviz dot content
'''

def prodid(prod):
    s = prod.name + '_' + prod.version
    return s.replace('-','_').replace(' ','_')

def simple(graph):
    ret = ['digraph G {',]

    for n in graph.nodes():
        ret.append('  %s [label="%s\\n%s"];' % (prodid(n), n.name, n.version))

    ret.append('')

    for t,h in graph.edges():
        ret.append('  %s -> %s;' % (prodid(t), prodid(h)))

    ret.append('}\n')
    return '\n'.join(ret)
