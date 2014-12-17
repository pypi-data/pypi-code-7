import pkg_resources
import yaml

from .environment import Environment

__version__ = pkg_resources.require('eggmonster')[0].version

logger_port = 13000

env = Environment()

def clear_defaults():
    env.clear_defaults()

def update_defaults(e):
    env.update_defaults(e)

def clear_locals():
    env.clear_locals()

def update_locals(e):
    env.update_locals(e)

def load_default_yaml(string='', file=None, sub=None):
    load_yaml(update_defaults, string=string, file=file, sub=sub)

def load_local_yaml(string='', file=None, sub=None):
    load_yaml(update_locals, string=string, file=file, sub=sub)

def load_yaml(loader, string='', file=None, sub=None):
    """Update the global env with the given YAML.

    If 'sub' is given, it should be a callable that returns
    a subkey of the loaded YAML; e.g. lambda x: x['bix']
    """
    if file:
        string = open(file).read()
    if string.strip():
        opts = yaml.load(string)
        if sub:
            opts = sub(opts)
        assert type(opts) is dict
        loader(opts)

_man_env = [False]

def managed_env():
    return _man_env[0]

def _set_managed_env():
    _man_env[0] = True
