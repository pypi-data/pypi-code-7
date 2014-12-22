
# python standard library
import os
import importlib
import inspect
import pkg_resources
import pkgutil


class RyeMother(object):
    """
    A gatherer of child classes
    """
    def __init__(self, exclusions='index.py __init__.py'.split(),
                 parent=None,
                 base_package=None,
                 group=None, name=None,
                 module=None,
                 keyfunction=None):
        """
        Rye Mother constructor

        :param:
        
         - `exclusions`: list of filenames to ignore
         - `parent`: class definiton for parent of classes to import
         - `base_package`: the top-level package (e.g. 'ape')
         - `group`: group-name from the setup.py entry_points
         - `name`: name of entry in group
         - `module`: name of module (to use instead of an entry point)
         - `keyfunction`: a function to transform the dictionary keys
        """
        self.parent = parent
        self.group = group
        self.name = name
        self.module = module
        self.exclusions = exclusions
        self.keyfunction = keyfunction
        self._base_package = base_package
        return

    @property
    def base_package(self):
        """
        The name of the top-level package
        """
        if self._base_package is None:
            self._base_package = __package__.split('.')[0]
        return self._base_package
        
    def __call__(self, parent=None, group=None, name=None,
                 modulename=None, keyfunction=None):
        """
        The main interface

        :param:

         - `parent`: parent class whose children to gather
         - `group`: [<group.name>] entry from setup.py entry_points
         - `name`: name given in the entry_point
         - `modulename`: name of a module (if this is given, group and name will be ignored)
         - `keyfunction`: function to transform the keys of the dict

        :return: dict of name:class definition
        """
        if parent is None:
            parent = self.parent
        if group is None:
            group = self.group            
        if name is None:
            name = self.name
        if keyfunction is None:
            if self.keyfunction is not None:
                keyfunction = self.keyfunction
            else:
                keyfunction = lambda s: s

        if modulename is None:
            return self.from_entry_point(parent, group, name, keyfunction)
        else:
            return self.from_module_name(parent=parent, modulename=modulename, keyfunction=keyfunction)
        return

    def from_module_name(self, parent, modulename, keyfunction):
        """
        Retrieves the definitions using the modulename (dot-notation: ape.plugins)

        :param:

         - `parent`: parent class whose children to gather
         - `modulename`: name of a module (if this is given, group and name will be ignored)       
         - `keyfunction`: function to transform the keys of the dict

        :return: dict of name:class definition
        """
        children = {}
        def is_child(candidate):
            # this is a filter for inspect.getmembers
            # returns True if candidate object has the correct parent class
            return hasattr(candidate, '__base__') and candidate.__base__ is parent

        module = importlib.import_module(modulename)
        members = inspect.getmembers(module,
                                    predicate=is_child)
        for member in members:
                name, definition = member
                children[name] = definition
        return children

    def from_entry_point(self, parent, group, name, keyfunction):
        """
        Retrieves the definitions using an entry-point
        
        :param:

         - `parent`: parent class whose children to gather
         - `group`: [<group.name>] entry from setup.py entry_points
         - `name`: name given in the entry_point
         - `keyfunction`: function to transform the keys of the dict

        :return: dict of name:class definition
        """        
        def is_child(candidate):
            # this is a filter for inspect.getmembers
            # returns True if candidate object has the correct parent class
            return hasattr(candidate, '__base__') and candidate.__base__ is parent

        children = {}

        module = pkg_resources.load_entry_point(self.base_package, group, name)
        dirname = os.path.dirname(module.__file__)
        prefix = module.__name__ + '.'
        names = (name for loader, name, is_pkg in pkgutil.iter_modules([dirname],prefix) if not is_pkg)
        modules = (importlib.import_module(name) for name in names)

        for module in modules:
            # members is a list of children in the module
            members = inspect.getmembers(module, predicate=is_child)
            for member in members:
                # member is a name, class definition tuple
                name, definition = member
                name = keyfunction(name)
                children[name] = definition
        return children
# end RyeMother    
