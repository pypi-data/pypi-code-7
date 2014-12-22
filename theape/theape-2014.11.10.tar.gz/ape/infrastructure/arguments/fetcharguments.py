
"""fetch subcommand
    
usage: ape fetch -h
       ape fetch [<name>...]  [--module <module> ...] 

positional arguments:
    <name>                         List of plugin-names (default=['Ape'])

optional arguments:
    -h, --help                     Show this help message and exit
    -m, --module <module> ...      Non-ape modules
"""


# the APE
from ape.infrastructure.arguments.arguments import BaseArguments
from ape.infrastructure.arguments.basestrategy import BaseStrategy
from ape.infrastructure.crash_handler import try_except


class FetchArgumentsConstants(object):
    """
    Constants for the `fetch` sub-command arguments
    """    
    __slots__ = ()
    # arguments and options
    names = "<name>"
    modules = '--module'
    
    # defaults
    default_names = ['Ape']


class Fetch(BaseArguments):
    """
    fetch a sample configuration
    """
    def __init__(self, *args, **kwargs):
        super(Fetch, self).__init__(*args, **kwargs)
        self.sub_usage = __doc__
        self._names = None
        self._modules = None
        self._function = None
        return

    @property
    def function(self):
        """
        fetch sub-command
        """
        if self._function is None:
            self._function = FetchStrategy().function
        return self._function

    @property
    def names(self):
        """
        List of plugin names to use
        """
        if self._names is None:
            self._names = self.sub_arguments[FetchArgumentsConstants.names]
            if not self._names:
                self._names = FetchArgumentsConstants.default_names
        return self._names

    @property
    def modules(self):
        """
        List of modules holding plugins
        """
        if self._modules is None:
            self._modules = self.sub_arguments[FetchArgumentsConstants.modules]
        return self._modules
    
    def reset(self):
        """
        Resets the attributes to None
        """
        super(Fetch, self).reset()
        self._modules = None
        self._names = None
        return
# end FetchArguments    


class FetchStrategy(BaseStrategy):
    """
    A strategy for the `fetch` sub-command
    """
    @try_except
    def function(self, args):
        """
        'fetch' a sample plugin config-file

        :param:

         - `args`: namespace with 'names' and 'modules' list attributes
        """
        for name in args.names:
            self.logger.debug("Getting Plugin: {0}".format(name))
            self.quartermaster.external_modules = args.modules
            plugin = self.quartermaster.get_plugin(name)
            # the quartermaster returns definitions, not instances
            try:
                config = plugin().fetch_config()
            except TypeError as error:
                self.logger.debug(error)
                if "Can't instantiate" in error[0]:
                    self.log_error(error="Plugin Implementation Error: ",
                                   message="{0}".format(error))
                else:
                    self.log_error(error="Unknown Plugin: ",
                                   message='{0}'.format(name))
        return
