
"""APE (the all-purpose-evaluator)

Usage: ape -h | -v
       ape [--debug|--silent] [--pudb|--pdb] <command> [<argument>...]
       ape [--debug|--silent] [--trace|--callgraph] <command> [<argument>...]

Help Options:

    -h, --help     Display this help message and quit.
    -v, --version  Display the version number and quit.
    
Logging Options:

    --debug   Set logging level to DEBUG.
    --silent  Set logging level to ERROR.

Debugging Options:

    --pudb       Enable the `pudb` debugger (if installed)
    --pdb        Enable the `pdb` (python's default) debugger
    --trace      Enable code-tracing
    --callgraph  Create a call-graph of for the code

Positional Arguments:

    <command>      The name of a sub-command (see below)
    <argument>...  One or more options or arguments for the sub-command
    
Available Sub-Commands:

    run    Run a plugin
    fetch  Fetch a sample configuration-file
    help   Display more help
    list   List known plugins
    check  Check a configuration

To get help for a sub-command pass `-h` as the argument. e.g.:

    ape run -h

"""     


# python standard library
import argparse

# third-party
import docopt

# this package
from ape import BaseClass, VERSION
from ape.infrastructure.ryemother import RyeMother


document_this = __name__ == '__builtin__'


class ArgumentsConstants(object):
    """
    Constants for the arguments
    """
    __slots__ = ()
    debug = "--debug"
    silent = '--silent'
    pudb = "--pudb"
    pdb = '--pdb'
    trace = '--trace'
    callgraph = '--callgraph'
    command = "<command>"
    argument = '<argument>'
# end ArgumentConstants    


class BaseArguments(BaseClass):
    def __init__(self, usage=__doc__, args=None, options_first=True, sub_usage=None):
        """
        BaseArguments constructor

        :param:

         - `usage`: usage string for `docopt`
         - `args`: list of arguments for `docopt`
         - `options_first`: docopt parameter to grab all options (or not)
         - `sub_usage`: usage string for sub-commands that inherit from this
        """
        super(BaseArguments, self).__init__()
        self._logger = None
        self.options_first = options_first
        self.usage = usage
        self.args = args
        self.sub_usage = sub_usage
        self._debug = None
        self._silent = None
        self._arguments = None
        self._pudb = None
        self._pdb = None
        self._trace = None
        self._callgraph = None

        self._command = None
        # for sub-commands that inherit from this
        self._sub_arguments = None
        return
    
    @property
    def command(self):
        """
        The sub-command requested
        """
        if self._command is None:
            self._command = self.arguments[ArgumentsConstants.command]
        return self._command
    
    @property
    def arguments(self):
        """
        Dictionary of arguments
        """
        if self._arguments is None:
            self._arguments = docopt.docopt(doc=self.usage,
                                            argv=self.args,
                                            options_first=self.options_first,
                                            version=VERSION)
        return self._arguments

    @property
    def debug(self):
        """
        Option to change logging level to debug

        :rtype: Boolean
        """
        if self._debug is None:
            self._debug = self.arguments[ArgumentsConstants.debug]
        return self._debug

    @property
    def silent(self):
        """
        Option to change logging level to error
        :rtype: Boolean
        """
        if self._silent is None:
            self._silent = self.arguments[ArgumentsConstants.silent]
        return self._silent

    @property
    def pudb(self):
        """
        Option to enable pudb debugger
        :rtype: Boolean
        """
        if self._pudb is None:
            self._pudb = self.arguments[ArgumentsConstants.pudb]
        return self._pudb

    @property
    def pdb(self):
        """
        Option to enable the python debugger
        :rtype: Boolean
        """
        if self._pdb is None:
            self._pdb = self.arguments[ArgumentsConstants.pdb]
        return self._pdb

    @property
    def trace(self):
        """
        Option to turn on code tracing
        :rtype: Boolean
        """
        if self._trace is None:
            self._trace = self.arguments[ArgumentsConstants.trace]
        return self._trace

    @property
    def callgraph(self):
        """
        Option to create a callgraph
        :rtype: Boolean
        """
        if self._callgraph is None:
            self._callgraph = self.arguments[ArgumentsConstants.callgraph]
        return self._callgraph

    @property
    def sub_arguments(self):
        """
        the sub-argument dictionary

        This isn't meant to be used by this class, this is for children

        :precondition: self.sub_usage set to sub-command __doc__
        """
        if self._sub_arguments is None:
            self._sub_arguments = docopt.docopt(doc=self.sub_usage,
                                                argv=[self.arguments[ArgumentsConstants.command]] +
                                                self.arguments[ArgumentsConstants.argument])
        return self._sub_arguments            


    def reset(self):
        """
        resets the properties to None
        """
        self._sub_arguments = None
        self._callgraph = None
        self._trace = None
        self._arguments = None
        self._debug = None
        self._silent = None
        self._pudb = None
        self._pdb = None
        self._command = None
        return
# end class BaseArguments    
