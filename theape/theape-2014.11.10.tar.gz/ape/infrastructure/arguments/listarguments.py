
"""list subcommand

usage: ape list -h
       ape list [<module> ...]

Positional Arguments:
  <module> ...  Space-separated list of importable module with plugins

optional arguments:

  -h, --help                 Show this help message and exit

"""


# the ape
from ape.infrastructure.crash_handler import try_except
from ape.infrastructure.arguments.arguments import BaseArguments
from ape.infrastructure.arguments.basestrategy import BaseStrategy


class ListArgumentsConstants(object):
    """
    Constants for the list sub-command arguments
    """
    __slots__ = ()
    # arguments
    modules = "<module>"


class List(BaseArguments):
    """
    list known plugins
    """
    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self._modules = None
        self.sub_usage = __doc__
        self._function = None
        return

    @property
    def function(self):
        """
        The `list` sub-command
        """
        if self._function is None:
            self._function = ListStrategy().function
        return self._function

    @property
    def modules(self):
        """
        List of external modules holding plugins
        """
        if self._modules is None:
            self._modules = self.sub_arguments[ListArgumentsConstants.modules]
        return self._modules

    def reset(self):
        """
        Resets the attributes to None
        """
        super(List, self).reset()
        self._modules = None
        return
# end List


class ListStrategy(BaseStrategy):
    """
    The strategy for the 'list' sub-command
    """    
    @try_except
    def function(self, args):
        """
        The function to run for this strategy (instead of the ArgParse sub-command function).
        Uses the QuarteMaster to list the plugins

        :param:

         - `args`: object with `modules` attribute
        """
        self.quartermaster.external_modules = args.modules
        self.quartermaster.list_plugins()
        return
