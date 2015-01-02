from base import HubComponent
from hub import Hub
import os
import constants


class Group(HubComponent):
    """
    Represents the groups file on disk.
    """

    params = constants.groups_fields

    def __init__(self, name, label=None, priority=None, defaultIsClosed=None):
        HubComponent.__init__(self)
        self.name = name
        if label is None:
            label = name
        self.label = label
        self.priority = priority
        self.defaultIsClosed = defaultIsClosed
        self._local_fn = None
        self._remote_fn = None

    def validate(self):
        for k in self.params:
            if getattr(self, k) is None:
                raise ValueError('Attribute %s is required' % k)

    @property
    def hub(self):
        hub, level = self.root(Hub)
        if level is None:
            return None
        if level != -2:
            raise ValueError(
                "Found a hub at %s levels away -- needs to be -2" % level)
        return hub

    @property
    def local_fn(self):
        if self._local_fn is not None:
            return self._local_fn
        if self.hub is None:
            return None
        return os.path.join(
            os.path.dirname(self.hub.local_fn),
            self.hub.hub + '.groups.txt')

    @local_fn.setter
    def local_fn(self, fn):
        self._local_fn = fn

    @property
    def remote_fn(self):
        if self._remote_fn is not None:
            return self._remote_fn
        if self.hub is None:
            return None
        return os.path.join(
            os.path.dirname(self.hub.remote_fn),
            self.hub.hub + '.groups.txt')

    @remote_fn.setter
    def remote_fn(self, fn):
        self._remote_fn = fn

    def __str__(self):
        s = []
        for k in self.params:
            v = getattr(self, k)
            if v is not None:
                s.append('%s %s' % (k, v))
        return '\n'.join(s)

    def _render(self):
        fout = open(self.local_fn, 'w')
        fout.write(str(self))
        fout.close()
        return fout.name
