"""
mineshaft
~~~~~~~~~

:copyright: (c) 2014 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""
from time import time
from operator import attrgetter
import requests

__all__ = ('Mineshaft', 'Node', 'LeafNode', 'BranchNode')


getkey = attrgetter('key')
HINTS = {'*', '[', '{', '?'}


def needs_resolved(path):
    """Test if a path is a pattern or is already fully qualified"""
    for c in path:
        if c in HINTS:
            return True
    return False


def is_leaf(node):
    return node.leaf


class Node(object):
    depth = 0
    leaf = False
    key = None

    def __repr__(self):
        return '<%s key=%r depth=%r>' % (type(self).__name__, self.key, self.depth)

    def __str__(self):
        return str(self.key)

    def __unicode__(self):
        return unicode(self.key)


def load(raw):
    if raw['Leaf']:
        node = LeafNode()
    else:
        node = BranchNode()
    node.depth = raw['Depth']
    node.key = raw['Key']
    return node


class LeafNode(Node):
    leaf = True


class BranchNode(Node):
    leaf = False


class Mineshaft(object):
    """Library for interacting with the mineshaft API"""

    def __init__(self, address='http://localhost:8080'):
        self.address = address.rstrip('/')
        self.session = requests.Session()

    def get(self, url, **kwargs):
        return self.session.get(self.address+url, **kwargs).json()

    def children(self, query=''):
        return self.to_nodes(self.get('/children', params={'query': query}))

    def resolve(self, query):
        return self.to_nodes(self.get('/paths', params={'query': query}))

    def metrics(self, targets, start_time=None, end_time=None):
        if start_time is None:
            start_time = int(time()) - 86400  # 24 hours ago
        if end_time is None:
            end_time = int(time())

        assert start_time > 0
        assert end_time > 0
        assert start_time < end_time

        if isinstance(targets, basestring):
            targets = [targets]

        targets = set(targets)
        unresolved = set(filter(needs_resolved, targets))
        resolved = targets - unresolved
        if unresolved:
            targets = resolved | set(map(getkey, filter(is_leaf, self.resolve(unresolved))))

        params = {'target': targets, 'from': start_time, 'to': end_time}
        return self.get('/metrics', params=params)

    def ping(self):
        try:
            r = self.get('/ping')
            return r['status'] == 200
        except Exception:
            return False

    def to_nodes(self, results):
        return [load(n) for n in results]
