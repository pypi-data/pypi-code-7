import os
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from validate import ValidationError
from hub import Hub
from base import HubComponent


class GroupsFile(HubComponent):
    def __init__(self, group=None):
        """
        Represents the groups file on disk.  Can contain multiple
        :class:`Group` objects, each of which represent a stanza in this
        file.

        The file ultimately created (with the self.render() method) will be
        determined by the parent Hub's `groups_filename` attribute.  By
        default, this is the hub name, plus ".groups.txt"
        """
        HubComponent.__init__(self)
        self._local_fn = None
        self._remote_fn = None
        if group is None:
            group = []
        for group in group:
            self.add_group(group)

    @property
    def hub(self):
        hub, level = self.root(Hub)
        if level is None:
            return None
        if level != -1:
            raise ValueError(
                "Found a hub at %s levels away -- needs to be -1" % level)
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

    def add_group(self, group):
        self.add_child(group)

    @property
    def groups(self):
        return [i for i in self.children if isinstance(i, group.group)]

    @property
    def groups(self):
        return [i for i in self.children if isinstance(i, groups.Groups)]

    def __str__(self):
        s = []
        for group in self.groups:
            s.append(str(group))
        return '\n'.join(s) + '\n'

    def _render(self):
        """
        Renders the children group objects to file
        """
        fout = open(self.local_fn, 'w')
        fout.write(str(self))
        fout.close()
        return fout.name

    def validate(self):
        if len(self.children) == 0:
            raise ValueError(
                "No defined group objects to use")
