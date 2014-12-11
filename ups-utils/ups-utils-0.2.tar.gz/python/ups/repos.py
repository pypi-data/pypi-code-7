#!/usr/bin/env python
'''
Interact with UPS repositories
'''

import os
from glob import glob
import shelve
import hashlib
import tarfile
import tempfile

import networkx as nx

from .commands import UpsCommands

from .products import make_product, upslisting_to_product
import ups.depend


class UpsRepo(object):
    '''A UpsRepo object embodies a snapshot of the state of a single UPS
    products area.

    It consists of:

    - a directory
    - a user script to setup to use the "ups" command in that area
    - a number of products

    '''

    def __init__(self, directory, cachedir = '~/.ups-util/cache/'):
        if not os.path.exists(directory):
            raise RuntimeError, 'No such directory: "%s"' % directory
        self.uc = UpsCommands(directory)
        self._repo_dir = directory
        self._cache_dir = os.path.expanduser(os.path.expandvars(cachedir))
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)
        self.tree = self._update()
        
    def _get_shelf(self, name = 'ups-repos'):
        return shelve.open(os.path.join(self._cache_dir, name))

    def _hash(self, products):
        sha = hashlib.sha1()
        for p in products:
            sha.update(str(p))
        return sha.hexdigest()

    def _update(self):
        '''
        Return tree of dependencies
        '''
        products = self.uc.avail()

        key = self._hash(products)
        shelf = self._get_shelf()
        dat = shelf.get(self._repo_dir, dict())
        if dat.get('hash',None) == key:
            shelf.close()
            return dat['tree']

        tree = nx.DiGraph()
        for pd in products:
            text = self.uc.depend(pd)
            ng = ups.depend.parse(text)
            tree.add_nodes_from(ng.nodes())
            tree.add_edges_from(ng.edges())
        
        dat = dict(hash = key, tree=tree)
        shelf[self._repo_dir] = dat
        shelf.close()
        return tree

    def available(self):
        '''
        Return a list of available products in this repository, according to UPS.
        '''
        return self.tree.nodes()

    def unpack(self, me, tarfilepath):
        '''
        Install the <tarball> corresponding to the ManifestEntry <me> to this repository.
        '''
        # test repo writability before getting started
        tmpfd, tmpnam = tempfile.mkstemp(prefix='.ups-util-test-write-', dir=self._repo_dir)
        os.close(tmpfd)
        os.remove(tmpnam)

        tf = tarfile.open(tarfilepath)
        tf.extractall(self._repo_dir)
        shelf = self._get_shelf('ups-manifests')
        shelf[me.tarball] = tf.getnames()
        return True
        


def first_avail(repos):
    '''
    Return a list of available products among the repos in a first-come first-serve basis.
    '''
    ret = list()
    seen = set()
    for repo in repos:
        for pd in repo.available():
            pvqf = pd[:4]
            if pvqf in seen:
                continue
            seen.add(pvqf)
            ret.append(pd)
    return ret

def first_pvqf(repos, package, version, qualifiers, flavor):
    '''
    Return the first matching product or non
    '''
    pvqf = (package, version, qualifiers, flavor)
    for repo in repos:
        for pd in repo.available(): # carries repo dir info
            if pd[:4] == pvqf:
                return pd

def squash_trees(repos):
    '''Return a tree which is the union of all repository trees with the
    repo directory ignored.  '''

    def strip(pd):
        return make_product(*pd[:4])

    stree = nx.DiGraph()
    for repo in repos:
        tree = repo.tree
        stree.add_nodes_from([strip(n) for n in tree.nodes()])
        stree.add_edges_from([(strip(t),strip(h)) for t,h in tree.edges()])
    return stree
