
from __future__ import print_function

# python standard library
import re
import os
from collections import OrderedDict

# third party
from configobj import ConfigObj
#from validate import Validator

# this package
from ape import BaseClass
import ape.infrastructure.arguments.arguments as basearguments
from ape.infrastructure.arguments.argumentbuilder import ArgumentBuilder
from ape.infrastructure.configurationmap import ConfigurationMap
from ape.components.component import Composite
from ape.parts.storage.filestorage import FileStorage

from base_plugin import BasePlugin
from ape.infrastructure.code_graphs import module_diagram, class_diagram
from ape.infrastructure.errors import ApeError, DontCatchError, ConfigurationError
from ape import APESECTION, MODULES_SECTION, BLUE_WARNING
import  ape.plugins.quartermaster
from ape.parts.countdown.countdown import INFO
#from ape.parts.countdown.countdown import CountdownTimer
import ape.parts.countdown.countdown
import ape.infrastructure.singletons as singletons
#from ape.infrastructure.timemap import RelativeTime, AbsoluteTime
from ape.infrastructure.timemap import time_validator

class OperatorConfigurationConstants(object):
    """
    constants for the OperatorConfiguration
    """
    __slots__ = ()
    # sections
    settings_section = 'SETTINGS'
    operations_section = 'OPERATIONS'
    plugins_section = "PLUGINS"

    # options
    repetitions_option = 'repetitions'
    config_glob_option = 'config_glob'
    total_time_option = 'total_time'
    end_time_option = 'end_time'
    subfolder_option = 'subfolder'
    modules_option = 'external_modules'
    timestamp_option = 'timestamp'
    plugin_option = 'plugin'
    
    # defaults
    default_repetitions = 1
    default_config_glob = None
    default_total_time = None
    default_end_time = None
    default_subfolder = None
    default_modules = None
    default_timestamp = None

    #extra
    file_storage_name = 'infrastructure'

config_spec = """
[SETTINGS]
config_glob = string(default=None)
repetitions = integer(default=1)
total_time = relative_time(default=None)
end_time = absolute_time(default=None)
subfolder = string(default=None)
external_modules = string_list(default=None)
timestamp = string(default=None)

[OPERATIONS]
__many__ = force_list

[PLUGINS]
 [[__many__]]
 plugin = string
"""

class OperatorConfigspec(object):
    """
    A configuration specification for the OperatorConfiguration
    """
    def __init__(self):
        self._configspec = None
        self._validator = None
        return

    @property
    def configspec(self):
        """
        A configspec that  matches the Operator's Configuration
        """
        if self._configspec is None:
            self._configspec = ConfigObj(config_spec.splitlines(),
                                         list_values=False,
                                         _inspec=True)
        return self._configspec

    @property
    def validator(self):
        """
        A validator with user-defined classes
        """
        if self._validator is None:
            self._validator = time_validator
        return self._validator

constants = OperatorConfigurationConstants

class OperatorConfiguration(BaseClass):
    """
    Extracts arguments for operators from the configuration
    """
    def __init__(self, source):
        """
        Operator Configuration constructor

        :param:

         - `source`: name of configuration file
        """
        super(OperatorConfiguration, self).__init__()
        self.source = source
        self._configuration = None
        self._configspec = None
        self._countdown_timer = None
        self._settings = None
        self._operation_names = None
        self._quartermaster = None
        self._operation_configurations = None
        self._operation_timer = None
        self._operator = None
        return

    @property
    def operator(self):
        """
        Operator composite built from the configuration
        """
        if self._operator is None:
            self._operator = Composite(identifier='Operator',
                                       error=ApeError,
                                       error_message='Operation Crash',
                                       component_category='Operation',
                                       time_remains=self.countdown_timer)
            for operation_configuration in self.operation_configurations:
                self._operator.add(operation_configuration.operation)
        return self._operator

    @property
    def operation_timer(self):
        """
        A countdown timer for operations to share (None if end_time not set)
        """
        if (self._operation_timer is None and
            self.settings[constants.end_time_option] is not None):
            self._operation_timer = CountdownTimer(end_time=self.settings[constants.end_time_option])
        return self._operation_timer

    @property
    def operation_configurations(self):
        """
        Generator of Operation Configurations
        """
        if self._operation_configurations is None:
            try:
                self._operation_configurations = []
                operations = self.configuration[constants.operations_section]
                if not operations:
                    self.logger.warning(BLUE_WARNING.format(thing="[OPERATIONS] section not found in configuration"))
                plugins_section = self.configuration[constants.plugins_section]
                
                if not plugins_section:
                    message = "[PLUGINS] section not found in configuration"
                    
                    if not operations:
                        self.logger.warning(BLUE_WARNING.format(thing=message))
                    else:
                        self.log_error("ConfigurationError",
                                       message)
                        self.log_error("ConfigurationError",
                                       "need plugins for {0}".format(operations.values()))
                        raise ConfigurationError(message)
                        
                else:
                    for operation_name, plugin_subsections in operations.iteritems():
                        self._operation_configurations.append(OperationConfiguration(plugins_section=plugins_section,
                                                    plugin_subsections=plugin_subsections,
                                                    operation_name=operation_name,
                                                    quartermaster=self.quartermaster,
                                                    countdown_timer=self.operation_timer))
            except KeyError:
                self._operation_configurations = []
        return self._operation_configurations
        

    @property
    def quartermaster(self):
        """
        QuarterMaster built with external_modules

        :side-effect: file storage singleton initialized
        """
        if self._quartermaster is None:
            modules = self.settings[constants.modules_option]
            self._quartermaster = ape.plugins.quartermaster.QuarterMaster(external_modules=modules)

            # plugins will pull the file storage so it has to be initiated            
            singletons.refresh()
            self.initialize_file_storage()
        return self._quartermaster

    @property
    def settings(self):
        """
        SETTINGS section from the configuration
        """
        if self._settings is None:
            self._settings = self.configuration[constants.settings_section]
        return self._settings    

    @property
    def countdown_timer(self):
        """
        CountdownTimer built from the configuration for the operator
        """
        if self._countdown_timer is None:
            definition = ape.parts.countdown.countdown.CountdownTimer

            repetitions = self.settings[constants.repetitions_option]
            end_time = self.settings[constants.end_time_option]
            total_time = self.settings[constants.total_time_option]
            
            self._countdown_timer = definition(repetitions=repetitions,
                                               end_time=end_time,
                                               total_time=total_time,
                                               log_level=INFO)
        return self._countdown_timer

    @property
    def configspec(self):
        """
        OperatorConfigspec
        """
        if self._configspec is None:
            self._configspec = OperatorConfigspec()
        return self._configspec

    @property
    def configuration(self):
        """
        ConfigObj built from `source`
        """
        if self._configuration is None:

            self._configuration = ConfigObj(self.source,
                                                configspec=self.configspec.configspec,
                                                file_error=True)
            self._configuration.validate(self.configspec.validator)

        return self._configuration

    def initialize_file_storage(self):
        """
        This has to be called before the plugins are built so the path will be set

        :postcondition: file-storage singleton with sub-folder from default section added as path
        """
        file_storage = ape.infrastructure.singletons.get_filestorage(name=constants.file_storage_name)
        subfolder = self.settings[constants.subfolder_option]
        timestamp = self.settings[constants.timestamp_option]
        
        if subfolder is not None:
            file_storage.path = subfolder
        if timestamp is not None:
            file_storage.timestamp = timestamp
        return

    def save_configuration(self, filename):
        """
        saves the configuration map to disk

        :param:

         - `filename`: name of original file to save to disk
        """
        file_storage = singletons.get_filestorage(name=FILE_STORAGE_NAME)
        # get the sub-folder (if given) and let the FileStorage mangle the name as needed
        # to prevent clobbering files

        filename, extension = os.path.splitext(filename)

        # the extension is changed so if the user is using a glob
        # and didn't provide a sub-folder the compiled file won't
        # get picked up on re-running the code
        filename += COMPILED_EXTENSION
        name = file_storage.safe_name(filename)
        self.configuration.filename = name
        self.configuration.write()
        return

# end class OperatorConfiguration

class OperationConfiguration(BaseClass):
    """
    a builder of plugins for operations
    """
    def __init__(self, plugins_section, plugin_subsections,
                 operation_name, quartermaster, countdown_timer=None):
        """
        OperationConfiguration builder

        :param:

         - `plugins_section`: dict with configuration (PLUGINS section)
         - `operation_name`: option in the identifier for the operation
         - `plugin_subsections`: list of sub-section-names for the plugins
         - `quartermaster`: QuarterMaster to retrieve plugins
         - `countdown_timer`: CountdownTimer for the operation composite
        """
        super(OperationConfiguration, self).__init__()
        self.plugins_section = plugins_section
        self.operation_name = operation_name
        self.plugin_subsections = plugin_subsections
        self.quartermaster = quartermaster
        self.countdown_timer = countdown_timer
        
        self._plugin_sections_names = None
        self._operation = None
        return

    @property
    def operation(self):
        """
        A composite of plugins
        """
        if self._operation is None:
            self._operation = Composite(identifier='operation',
                                        error=DontCatchError,
                                        error_message="{0} Crash".format(self.operation_name),
                                        component_category=self.operation_name,
                                        time_remains=self.countdown_timer)
            for section, name in self.plugin_sections_names.iteritems():                
                try:
                    definition = self.quartermaster.get_plugin(name)
                    plugin = definition(configuration=self.plugins_section,
                                        section_header=section).product
                    self._operation.add(plugin)
                    if plugin is None:
                        raise ApeError("Unable to build plugin: {0} in section {1}".format(name,
                                                                                           section))
                except TypeError as error:
                    self.logger.info(error)
                    raise ConfigurationError("Could not find '{0}' plugin".format(name))
        return self._operation

    @property
    def plugin_sections_names(self):
        """
        creates a dict of plugin section-name:plugin-name pairs

        """
        if self._plugin_sections_names is None:
            names = (self.plugins_section[section][constants.plugin_option]
                     for section in self.plugin_subsections)
            self._plugin_sections_names = dict(zip(self.plugin_subsections,
                                                   names))
        return self._plugin_sections_names
        
# end class OperationConfiguration

in_pweave = __name__ == '__builtin__'

COMPILED_EXTENSION = '.compiled'
FILE_STORAGE_NAME = 'infrastructure'

CONFIGURATION = '''[OPERATIONS]
# the option names are just identifiers
# they will be executed in the order given.
# Each plugin has to have a corresponding section below
# e.g. if there is a `Sleep1` plugin listed as a right-hand-side value
# Then there needs to be a [[Sleep1]] section in the [PLUGINS] section
# to configure it
<option_name_1> = <comma-separated-list of plugins>
<option_name_2> = <comma-separated-list of plugins>
...
<option_name_n> = <comma-separated-list of plugins>

#[SETTINGS]
# these are settings for the overall operation

# if you add a configuration-file-glob (config_glob),
# all matching files will be added to the configuration
# (the default is None)
#config_glob = settings*.config

# if you want to repeat the operation defined in this config, give it repetitions
# (default is 1)
# repetitions = 1000000

# If you want to put a time limit after which to quit (this overrides repetitions)
# (default is None)
# total_time = 1 day 3 hours

# if you want to put an end time (this will override repetitions and total time):
# (default is None)
# end_time = November 23, 2013 8:00 am

# if you want to store files in a sub-folder
# (default is None)
# subfolder = <name>

# if one or more plugins is coming from the ape
# tell me which module to import it from
# comma-separated list
# (default is None)
# external_modules = package.module, package2.module2

# if you want to override the file timestamp format
# (default is None)
# timestamp = <strftime-formatted timestamp>

#[PLUGINS]
# for each plugin listed in the [OPERATIONS] there has to be a matching
# subsection below this section
# sub-sections are denoted by double-brackets (you can indent them too)
# the actual class name for the plugin is set with the 'plugin' option
# the rest of each plugin sub-section has to be whatever configures the plugin

#  [[plugin1]]
#  plugin = Sleep
#  updates_section = <section_name>
#  <sleep configuration>

#  [[plugin2]]
#  plugin = Iperf
#  <Iperf configuration>
'''

output_documentation = __name__ == '__builtin__'

if in_pweave:
    this_file = os.path.join(os.getcwd(), 'apeplugin.py')
    module_diagram_file = module_diagram(module=this_file, project='apeplugin')
    print(".. image:: {0}".format(module_diagram_file))

EXAMPLES = '''
ape run ape.ini
ape help
ape fetch
ape list'''

class Ape(BasePlugin):
    """
    The default plugin (provides the front-end for the APE)
    """
    def __init__(self, configfiles=None, *args, **kwargs):
        """
        Ape plugin Constructor

        :param:

         - `configfiles`: list of config-files to build product (Hortator Composite)
        """
        super(Ape, self).__init__(*args, **kwargs)
        self.configfiles = configfiles
        self._arguments = None
        return

    @property
    def arguments(self):
        """
        The ArgumentBuilder (used to set up the help-string)
        """
        if self._arguments is None:
            self._arguments = ArgumentBuilder()
        return self._arguments

    @property
    def sections(self):
        """
        An ordered dictionary for the HelpPage
        """
        if self._sections is None:
            bold = '{bold}'
            reset = '{reset}'
            
            name = __package__.split('.')[0]
            bold_name = bold + name + reset
            program = name + '[.\w]*'
            expression = re.compile(program)

            # get sample usage text
            arg_string = basearguments.__doc__.replace('Usage: ', '')
            

            # the main parser doesn't show help for the sub-commands (just --debug, --pudb, etc.)
            # so they are pulled separately
            argument_definitions = ArgumentBuilder().argument_definitions
            for definition in argument_definitions.itervalues():
                arg_string += '-' * 40 + '\n'
                arg_string +=  expression.sub(bold_name,
                                              definition().sub_usage.replace('Usage: ', ''))
            
            self._sections = OrderedDict()
            self._sections['Name'] = '{blue}' + name + reset + ' -- a plugin-based code runner'
            self._sections['Synopsis'] = arg_string
            self._sections['Description'] = bold_name + (' is the main code-runner. When it is run it looks'
                                                         ' for a configuration file or list of configuration files. '
                                                         'Within each file it looks for an [{0}] section. Each entry'
                                                         ' in that section is interpreted to be a list of plugins to '
                                                         'execute in top-down, left-right ordering.'.format(APESECTION))
            self._sections["Configuration"] = CONFIGURATION
            self._sections['Examples'] = 'ape run *.ini\nape help\nape fetch\nape list\nape check *ini'
            self._sections['Errors'] = '{bold}Oops, I crapped my pants:{reset} unexpected error (probably indicates implementation error)'
            self._sections['subcommands'] = ("help (this help), fetch (sample configuration), "
                                             "run <configuration-file(s)>, list (known plugins), check (configuration)")
            self._sections['Files'] = __file__
        return self._sections
    
    @property
    def product(self):
        """
        This is the Hortator Composite product

        :precondition: self.configfiles has been set 
        :return: hortator built from self.configfiles
        """
        #create a hortator
        hortator = Composite(error=Exception,
                             identifier='Hortator',
                             error_message="Operator Crash",
                             component_category='Operator')
        # Set the TimeTracker level to info so it outputs to the screen
        hortator.time_remains.log_level = INFO
        
        # traverse the config-files to get Operators and configuration maps
        for config_file in self.configfiles:
            # each APE config gets its own Operator
            operator_config = OperatorConfiguration(config_file)
            operator = operator_config.operator
            
            hortator.add(operator)
            
            # save the configuration as a copy so there will be a record
            operator_config.save_configuration(config_file)
        return hortator
        
    def fetch_config(self):
        """
        Prints example configuration to stdout
        """
        print(CONFIGURATION)
# end class Ape
