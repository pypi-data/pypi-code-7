import json
import collections
from pkg_resources import resource_filename


class Config(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self.cfg_path = resource_filename(__name__, 'config.json')
        self.__readcfg__()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        self.__readcfg__()
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value
        self.__writecfg__()

    def __delitem__(self, key):
        del self.store[key]
        self.__writecfg__()

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __readcfg__(self):
        try:
            self.store = json.loads(open(self.cfg_path, 'r').read())
        except IOError:
            self.store = dict()

    def __writecfg__(self):
        with open(self.cfg_path, 'w') as f:
            json.dump(self.store, f, indent=4, separators=(',', ': '),
                      sort_keys=True)
