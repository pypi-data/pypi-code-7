#!/usr/bin/env python
'''
Define general objects used throughout the ups. namespace.
'''

from collections import namedtuple

def Node(payload = None, children = None, **kwds):
    N = namedtuple("Node", 'payload children params')
    return N(payload or list(), children or list(), kwds)


def argify_proddesc(pd):
    s = pd.name + ' ' + pd.version
    if pd.flavor:
        s += ' -f ' + pd.flavor
    if pd.repo:
        s += ' -z ' + pd.repo
    if pd.quals:
        s += ' -q ' + pd.quals
    return s

def ProdDesc(name, version='', flavor="", repo="", quals=""):
    PD = namedtuple("ProdDesc",'name version flavor repo quals')
    PD.upsargs = argify_proddesc

    return PD(name,version,flavor,repo,quals)

def parse_proddesc(string):
    'Convert from "pkg ver -f flav -z repo -q quals" to a ProdDesc'
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-f',dest='flavor', default='')
    parser.add_option('-z',dest='repo', default='')
    parser.add_option('-q',dest='quals', default='')

    args = string.split()
    o,a = parser.parse_args(args)
    pkg = a[0]
    try:
        ver = a[1]
    except IndexError:
        ver = ''
    pd = ProdDesc(pkg, ver, o.flavor, o.repo, o.quals)
    return pd

def parse_prodlist(text):
    '''
    Convert the output of "ups list" to list of ProdDesc
    '''
    ret = list()
    for line in text.split('\n'):
        line =line.strip()
        if not line: continue
        ver,pkg,flav,quals,repo = [x.replace('"','') for x in line.split()]
        p = ProdDesc(ver,pkg,flav,repo,quals)
        ret.append(p)
    return ret

    
