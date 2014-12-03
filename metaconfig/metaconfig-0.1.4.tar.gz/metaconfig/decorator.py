"""
Inject default values into functions and methods using decorators.

"""

import inspect

class Error(Exception):
    pass

class ConfigDecorator(object):
    """
    Container for decorators that inject default values from a particular
    metaconfig configuration and optional section into functions and
    methods.

    """
    def __init__(self, config, section=None):
        self.config = config
        self.section = section
        self.filters = {}

    def set_defaults(self, section=None, exclude=None, include=None):
        """
        A decorator to set defaults from metaconfig.

        This decorator is destructive, in that it manipulates the
        decorated function/method and returns it.  Use with_defaults
        to use the wrapping style.

        """
        if section is None:
            section = self.section
        if section is None:
            raise Error("No section specified")

        def dec(func):
            # Deduce new defaults
            args, varargs, kwargs, defaults = inspect.getargspec(func)
            argdict = dict(self.config.items(section))
            new_defaults = []
            if defaults:
                first_default = len(args) - len(defaults)
            else:
                first_default = None
            for n, arg in enumerate(args):
                val = None
                if arg in argdict:
                    val = argdict[arg]
                elif first_default and n >= first_default:
                    val = defaults[n-first_default]

                if val is None and new_defaults:
                    # If default arguments have already started raise an Exception
                    raise Error("non-default argument follows configured default argument")

                if include and arg not in include:
                    continue
                if exclude and arg in exclude:
                    continue
                new_defaults.append(self._filter_default(section, arg,
                                                         val))

            # Set defaults tuple (depends on method or function)
            try:
                func.func_defaults = tuple(new_defaults)
            except AttributeError:
                try:
                    func.im_func.func_defaults = tuple(new_defaults)
                except AttributeError:
                    raise Error("Couldn't find defaults of decorated object")

            return func

        return dec
        
    def with_defaults(self, section=None, exclude=None, include=None):
        """
        A decorator to set defaults from metaconfig.

        This decorator is non-destructive.  It returns a function
        wrapping the decorated function/method.

        """
        raise NotImplementedError

    def set_filter(self, section=None, option=None, filter=None):
        """
        Set a filter function for a particular option.

        """
        if section is None:
            section = self.section
        if section is None:
            raise Error("No section specified")

        if option is None:
            raise Error("No option specified")

        fsec = self.filters.setdefault(section, {})
        fsec[option] = filter

    def _filter_default(self, section, option, default):
        try:
            filter = self.filters[section][option]
            return filter(default)
        except KeyError:
            return default
