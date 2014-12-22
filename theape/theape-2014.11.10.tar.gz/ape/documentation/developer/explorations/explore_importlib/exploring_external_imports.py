
# python standard library
import importlib
import inspect

# ape
from ape.plugins.base_plugin import BasePlugin


module_name = 'fakepackage.fakeplugin'
module = importlib.import_module(module_name)
members = inspect.getmembers(module,
                             lambda o: inspect.isclass(o) and
                             o.__base__ is BasePlugin)
for member in members:
    name, definition = member
    print name
    d = definition()
    d.fetch_config()
