
from __future__ import print_function


# python standard library
from collections import OrderedDict
import textwrap
import importlib

# third party
from configobj import ConfigObj
from validate import Validator

# this package
from base_plugin import BasePlugin, BaseConfiguration
from ape.parts.dummy.dummy import DummyClass
from ape.parts.dummy.dummy import CrashDummy
from ape.parts.dummy.dummy import HangingDummy


DESCRIPTION = """{bold}DummyClass{reset} logs its calls and then returns. It is meant to be used as changes are made to the infrastructure so that the {blue}Ape{reset} can be tested without using any other components."""
EXAMPLES = """{bold}dummy(){reset}"""
NOTE = "The {bold}DummyClass{reset} will change as the infrastructure changes. In particular the building and testing of plugins and components will likely evolve once real plugins are created."


output_documentation = __name__ == '__builtin__'


class Dummy(BasePlugin):
    """
    A plugin to test the infrastructure (a no-op)
    """
    def __init__(self, *args, **kwargs):
        super(Dummy, self).__init__(*args, **kwargs)
        return

    @property
    def sections(self):
        """
        An ordered dict for the help page
        """
        if self._sections is None:
            bold = "{bold}"
            reset = '{reset}'
            
            self._sections = OrderedDict()
            self._sections['Name'] = (bold + 'DummyClass' + reset +
                                        ' -- a no-op')
            self._sections['Description'] = DESCRIPTION
            self._sections['Example'] = EXAMPLES
            self._sections['Note'] = NOTE
        return self._sections

    @property
    def product(self):
        """
        builds and returns a DummyClass

        :precondition: self.configuration map has been set
        """
        if self._product is None:
            kwargs = self.configuration[self.section_header]
            self._product = DummyClass(**kwargs)
        return self._product

    def fetch_config(self):
        """
        prints a sample configuration
        """
        print(textwrap.dedent("""
        [[DUMMY]]
        # the section name is arbitrary but must match the name in the [APE] section
        # so the 'plugin' option is what actually specifies the plugin 
        plugin = Dummy
        # the dummy will take anything you set here and log it
        any_arbitrary_option = any_arbitrary_value
        another_option = another_value"""))
        return
# end class Dummy


class CrashTestDummyConstants(object):
    __slots__ = ()
    error_module_option = 'error_module'
    error_option = 'error'
    error_message_option = 'error_message'
    function_option = 'function'
    
    error_module_default = 'exceptions'
    error_default = 'Exception'
    error_message_default = 'My work is done, why wait?'
    function_default = '__call__'


crash_configspec = """
plugin = option('CrashTestDummy')

error_module = string(default='exceptions')
error = string(default='Exception')
error_message = string(default='My work is done, why wait?')
function = string(default='__call__')
"""


class CrashTestDummyConfiguration(BaseConfiguration):
    """
    Translates the configobj configuration to a CrashTestDummy
    """
    def __init__(self, *args, **kwargs):
        """
        CrashTestDummyConfiguration

        :param:

         - `section_name`: name in the configuration with settings
         - `configuration`: dict of configuration values
        """
        super(CrashTestDummyConfiguration, self).__init__(*args, **kwargs)
        return

    @property
    def configspec_source(self):
        """
        the configuration specification source
        """
        if self._configspec_source is None:
            self._configspec_source = crash_configspec
        return self._configspec_source

    @property
    def product(self):
        """
        A crash test dummy
        """
        if self._product is None:
            error_module = self.configuration['error_module']
            error = self.configuration['error']
            module = importlib.import_module(error_module)
            err = getattr(module, error)
            self.configuration['error'] = err
            self._product = CrashDummy(**self.configuration)
        return self._product
# end class CrashTestDummyConfiguration    


class CrashTestDummy(BasePlugin):
    """
    A plugin to test the infrastructure by crashing
    """
    def __init__(self, *args, **kwargs):
        super(CrashTestDummy, self).__init__(*args, **kwargs)
        self._config_builder = None
        return

    @property
    def config_builder(self):
        """
        A CrashTestDummy configuration
        """
        if self._config_builder is None:
            self._config_builder = CrashTestDummyConfiguration(section_name=self.section_header,
                                                               source=self.configuration)
        return self._config_builder

    @property
    def sections(self):
        """
        An ordered dict for the help page
        """
        if self._sections is None:
            bold = "{bold}"
            reset = '{reset}'
            
            self._sections = OrderedDict()
            self._sections['Name'] = (bold + 'CrashTestDummy' + reset +
                                        ' -- a crashing module')
            self._sections['Description'] = (DESCRIPTION.replace('DummyClass',
                                                                'CrashTestDummy') +
                "\It takes an error to raise as an argument and raises it when called.")
            self._sections['Example'] = EXAMPLES.replace('dummy',
                                                         'crashtestdummy')
            self._sections['Note'] = NOTE
        return self._sections

    @property
    def product(self):
        """
        builds and returns a CrashTestDummy

        :precondition: self.configuration map has been set
        :return: CrashTestDummy
        """
        if self._product is None:
            self._product = self.config_builder.product
        return self._product

    def fetch_config(self):
        """
        prints a message saying there is no configuration
        """
        print(textwrap.dedent("""
        [[CRASHTESTDUMMY]]
        plugin = CrashTestDummy
        # the dummy will take anything you set here and log it
        any_arbitrary_option = any_arbitrary_value
        another_option = another_value

        # but these will set the error to raise
        # if these are missing will default to Exception
        error_message = AUUUUUUUGGGGGHHHHHHH
        error_module = exceptions
        error = RuntimeError

        # to have it crash somewhere specific in the component interface
        # can be any attribute you want to call
        # e.g. function = umma will crash if dummy.umma() is called or dummy.umma
        function = __call__"""))
        return
# end class CrashTestDummy


stuck_dummy_configspec = """
plugin = option('StuckDummy)

__many__ = string
"""


class StuckDummyConfiguration(BaseConfiguration):
    """
    Configuration builder for the dummy that hangs

    :param:

         - `section_name`: name in the configuration with settings
         - `configuration`: dict of configuration values

    """
    def __init__(self, *args, **kwargs):
        super(StuckDummyConfiguration, self).__init__(*args, **kwargs)
        return

    @property
    def configspec_source(self):
        """
        configuration specification source
        """
        if self._configspec_source is None:
            self._configspec_source = stuck_dummy_configspec
        return self._configspec_source

    @property
    def product(self):
        """
        The HangingDummy callable object
        """
        if self._product is None:
            self._product = HangingDummy(**self.configuration)
        return self._product
# end class StuckDummyConfiguration    


class StuckDummy(BasePlugin):
    """
    A plugin to test the infrastructure by hanging
    """
    def __init__(self, *args, **kwargs):
        super(StuckDummy, self).__init__(*args, **kwargs)
        self._config_builder = None
        return

    @property
    def config_builder(self):
        """
        Stuck Dummy Configuration 
        """
        if self._config_builder is None:
            self._config_builder = StuckDummyConfiguration(source=self.configuration,
                                                           section_name=self.section_header)
        return self._config_builder

    @property
    def sections(self):
        """
        An ordered dict for the help page
        """
        if self._sections is None:
            bold = "{bold}"
            reset = '{reset}'
            
            self._sections = OrderedDict()
            self._sections['Name'] = (bold + 'StuckDummy' + reset +
                                        ' -- a stuck (hanging) module')
            self._sections['Description'] = (DESCRIPTION.replace('DummyClass',
                                                                'StuckDummy') +
                "Sleeps for three years at a time in an infinite loop.")
            self._sections['Example'] = EXAMPLES.replace('dummy',
                                                         'stuckdummy')
            self._sections['Note'] = NOTE
        return self._sections

    @property
    def product(self):
        """
        builds and returns a HangingDummy

        :precondition: self.configuration map has been set
        """
        if self._product is None:
            # get the random inputs and create a keyword-argument- dictionary
            self._product = self.config_builder.product            
        return self._product

    def fetch_config(self):
        """
        prints a message saying there is no configuration
        """
        print(textwrap.dedent("""
        [[HANGINGDUMMY]]
        # the dummy will take anything you set here and log it
        any_arbitrary_option = any_arbitrary_value
        another_option = another_value
        """))
        return
# end class HangingDummy
