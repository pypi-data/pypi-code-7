
# python standard library
import inspect

# this package
import dummy


print inspect.getdoc(dummy)


print inspect.getdoc(dummy.DummyClass)


print inspect.getdoc(dummy.DummyClass.a_tuple)


from dummy import DummyClass
d = DummyClass(a=1)
print inspect.getfile(DummyClass)

try:
    print inspect.getfile(d)
except TypeError as error:
    print error


print inspect.getargspec(DummyClass.convoluted)


print inspect.getmembers(dummy, inspect.isclass)


print inspect.getmembers(dummy, lambda o: inspect.isclass(o) and o.__name__.startswith('Dummy'))


print inspect.getmembers(dummy, lambda o: inspect.isclass(o) and o.__base__ is DummyClass)


import os
import importlib

from dummy import PluginBase

for filename in os.listdir(os.getcwd()):
    # the print statements in this module are showing up in the output when I import it
    if filename.endswith('.py') and not filename=='explore_inspect.py':
        base, extension = os.path.splitext(filename)
        try:
            candidate = importlib.import_module(base)
        except ImportError as error:
            # for some reason nose is using /usr/lib/python2.7/importlib
            # and this is causing it to fail
            print error
            continue        
        members = inspect.getmembers(candidate, lambda o: inspect.isclass(o) and o.__base__ is PluginBase)
        for member in members:
            name, definition = member
            print name
            m = definition()
            print 'Help:'
            print m.help_string
            print "Config:"
            print m.config
            print "Product:"
            print m.product
