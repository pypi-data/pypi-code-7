# -*- coding: utf-8 -*-
from operator import itemgetter
from inspect import currentframe

import Acquisition
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getUtility
from plone.uuid.interfaces import IUUID


# noinspection PyUnresolvedReferences
def iter_pos_chain(container_, id__, cache, seen):
    if getattr(Acquisition.aq_base(container_),
               'getObjectPosition', None):
        yield container_.getObjectPosition(id__)
    else:
        yield 0

    parent_ = Acquisition.aq_parent(container_)

    uuid = IUUID(container_, None)
    if uuid in seen:
        return

    if uuid in cache:
        for value in cache[uuid]:
            yield value

    else:
        if hasattr(Acquisition.aq_base(parent_),
                   'getObjectPosition'):
            for p in iter_pos_chain(parent_,
                                    container_.getId(),
                                    cache, seen + [uuid]):
                cache.setdefault(uuid, []).append(p)
                yield p


# noinspection PyUnresolvedReferences
def documentToKeyMap(self):
    # we need to get the containers in order to get the respective
    # positions of the search results, but before that we need those
    # results themselves.  luckily this is only ever called from
    # `sortResults`, so we can get it form there.  oh, and lurker
    # says this won't work in jython, though! :)
    rs = currentframe(1).f_locals['rs']
    rids = {}
    items = []
    containers = {}
    getpath = self.catalog.paths.get
    traverse = getUtility(ISiteRoot).unrestrictedTraverse
    for rid in rs:
        path = getpath(rid)
        parent, id_ = path.rsplit('/', 1)
        container = containers.get(parent)
        if container is None:
            containers[parent] = container = traverse(parent)
        rids[id_] = rid              # remember in case of single folder
        items.append((rid, container, id_))  # or else for deferred lookup
    pos = {}
    if len(containers) == 1:
        # the usual "all from one folder" case can be optimized
        folder = containers.values()[0]
        if getattr(Acquisition.aq_base(folder),
                   'getOrdering', None):
            ids = folder.getOrdering().idsInOrder()
        else:
            # site root or old folders
            ids = folder.objectIds()
        for idx, id_ in enumerate(ids):
            rid = rids.get(id_)
            if rid:
                pos[rid] = idx
        return pos
    else:
        # otherwise the entire map needs to be constructed...
        chain_cache = {}
        for rid, container, id_ in items:
            pos[rid] = tuple(reversed(tuple(
                iter_pos_chain(container, id_, chain_cache, [])))) + (rid,)

        chain_order_key = lambda x: itemgetter(*list(range(len(x) - 1)))(x)
        chain_order = sorted(pos.values(), key=chain_order_key)

        for rid in pos:
            pos[rid] = chain_order.index(pos[rid])

        return pos
