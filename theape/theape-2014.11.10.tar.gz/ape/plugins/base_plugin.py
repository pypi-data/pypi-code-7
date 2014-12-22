
# python standard library
from __future__ import print_function
from abc import ABCMeta, abstractmethod, abstractproperty
import os
from types import StringType

# third party
from configobj import ConfigObj, flatten_errors, get_extra_values
from validate import Validator

# this package 
from ape.infrastructure.baseclass import BaseClass
from ape.parts.helppage.helppage import HelpPage
from ape.infrastructure.code_graphs import module_diagram, class_diagram
from ape.infrastructure.errors import ConfigurationError


in_pweave = __name__ == '__builtin__'


class BasePlugin(BaseClass):
    """
    An abstract base-class for plugins

    :param:

     - `configuration`: configuration-map for plugin configuration
    """
    __metaclass__ = ABCMeta
    def __init__(self, configuration=None, section_header=None):
        """
        BasePlugin constructor

        :param:

         - `configuration`: a ConfigObj for the product
         - `section_header`: header in the configuration for this plugin's info
        """
        super(BasePlugin, self).__init__()
        self._logger = None
        self._help = None
        self._config = None
        self._product = None
        self._help_page = None        
        self._sections = None
        self.configuration = configuration
        self.section_header = section_header
        return

    @abstractproperty
    def sections(self):
        """
        A (ordered) dictionary for the help page
        """
        return self._sections

    @property
    def help_page(self):
        """
        A HelpPage to use if self.sections has been defined
        """
        if self._help_page is None and self.sections is not None:
            self._help_page = HelpPage(sections=self.sections)
        return self._help_page                        

    def help(self, width=80):
        """
        Prints a help-string for the plugin

        :param:

         - `width`: number of characters wide to print help
        """
        if self.sections is None:
            print("'{0}' offers you no help. Such is life.".format(self.__class__.__name__))
        else:
            self.help_page.wrap = width
            self.help_page()
        return

    @abstractproperty
    def product(self):
        """
        Abstract Property: The plugin (Component implementation)
        """
        return

    @abstractmethod
    def fetch_config(self):
        """
        Abstract Method: Get sample config-file snippet required by this plugin
        """
        return   
# end class BasePlugin                


class SubConfigurationConstants(object):
    """
    Holder of SubConfiguration constants
    """
    __slots__ = ()
    plugin_option ='plugin'
    updates_section_option = 'updates_section'
    error_name = 'ConfigurationError'
    bad_option_message = "Option '{option}' in section '{section}' failed validation (error='{error}', should be {option_type})"
    missing_option_message = "Option '{option}' in section '{section}' of type {option_type} for plugin '{plugin}' required but missing"
    missing_section_message = "Section '{section}' to configure '{plugin}' not found in configuration"
    missing_plugin_option_message = "'plugin' option missing in section '{0}'"
    missing_plugin_replacement = "<non-plugin>"
    extra_message = "Extra {item_type} in section '{section}. '{name}'"
    check_rep_failure_message = "Errors in section [{0}] in the configuration"


class SubConfiguration(BaseClass):
    """
    Abstract base class for configurations
    """
    __metaclass__ = ABCMeta
    def __init__(self, source, section_name, allow_extras=False,
                 configspec_source=None, 
                 updatable=True, constants=None):
        """
        SubConfiguration constructor

        :param:

         - `source`: ConfigObj section
         - `section_name`: section-name in the configuration
         - `allow_extras`: if True, check_rep only raises errors on error
         - `configspec_source`: string with configuration specification (use to override the default)
         - `updatable`: if True, allows updating from other sections
         - `constants`: object with same properties as SubConfigurationConstants
        """
        super(SubConfiguration, self).__init__()
        self._constants = constants
        self.section_name = section_name
        self.allow_extras = allow_extras
        self.source = source
        self.updatable = updatable
        self._configspec_source = configspec_source
        self._sample = None
        self._validator = None
        self._configspec = None
        self._configuration = None
        self._plugin_name = None
        self._validation_outcome = None
        self._constants
        return

    @abstractproperty
    def configspec_source(self):
        """
        abstract: implement as configspec string
        """

    @property
    def sample(self):
        if self._sample is None:
            sample = self.configspec_source.lstrip('\n')
            sample = sample.replace('[', '[[[')
            sample = sample.replace(']', ']]]')
            self._sample = '[[{0}]]\n'.format(self.section_name) + sample
        return self._sample

    @property
    def constants(self):
        """
        object with string constants (see SubConfigurationConstants)
        """
        if self._constants is None:
            self._constants = SubConfigurationConstants
        return self._constants

    @property
    def validation_outcome(self):
        """
        Outcome of validating the configuration
        """
        if self._validation_outcome is None:
            self._validation_outcome = self.configuration.validate(self.validator,
                                                                   preserve_errors=True)
        return self._validation_outcome

    @property
    def plugin_name(self):
        """
        Gets the plugin name from the section

        :return: plugin-name if found or '<non-plugin>'
        """
        if self._plugin_name is None:        
            try:
                self._plugin_name = self.configuration[self.constants.plugin_option]
            except KeyError as error:
                self.logger.debug(error)
                self.logger.warning(self.constants.missing_plugin_option_message.format(self.section_name))
                #raise ConfigurationError(self.constants.missing_plugin_option_message.format(self.section_name))
                self._plugin_name = self.constants.missing_plugin_replacement
        return self._plugin_name

    @property
    def validator(self):
        """
        validator for the configuration
        """
        if self._validator is None:
            self._validator = Validator()
        return self._validator

    @property
    def configspec(self):
        """
        A configspec built from configspec_source for validation
        """
        if self._configspec is None:
            # avoiding side-effects if there's a splitlines call
            configspec_source = self.configspec_source
            
            if type(self.configspec_source) is StringType:
                configspec_source = configspec_source.splitlines()
            self._configspec = ConfigObj(configspec_source,
                                         list_values=False,
                                         _inspec=True)
        return self._configspec
            
    @property
    def configuration(self):
        """
        validates and sets the configuration using the source configuration

        :precondition: self.configspec has full configspec including section name
        :return:  validated configuration for this section
        """
        if self._configuration is None:
            section = ConfigObj(self.source[self.section_name],
                                    configspec=self.configspec,
                                    file_error=True)        
            if self.updatable:
                section = self.update(section)

            self._configuration = section

            # validation has to come after updating for ``update`` to work
            self._validation_outcome = self._configuration.validate(self.validator,
                                                                    preserve_errors=True)
        return self._configuration

    def update(self, section):
        """
        Uses 'updates_section' to build configuration from other section

        :param:

         - `section`: plugin-section to update

        :return: section merged with this section or original if appropriate 
        """
        if (self.constants.updates_section_option in section
            and section[self.constants.updates_section_option] is not None ):       
            other_section = section[self.constants.updates_section_option]
            base_section = ConfigObj(self.source[other_section],
                                     configspec=self.configspec)
            base_section.merge(section)
            section = base_section
        return section
        
    def process_errors(self):
        """
        processes configuration, validation_outcome and logs the errors

        :return: True if there were errors (same as `not self.validation_outcome`)
        """
        flattened_errors = flatten_errors(self.configuration,
                                           self.validation_outcome)

        for sections, option, error in flattened_errors:
            section = ",".join(sections)
            if len(section):
                section = "{0},{1}".format(self.section_name, section)
            else:
                section = self.section_name

            if option is not None: # something is wrong with the option
                # if there are sub-sections then the configspec has to be traversed to get the option-type
                spec = self.configspec
                try:
                    for section in sections:
                        spec = spec[section]                
                    option_type = spec[option]
                except KeyError as error:
                    self.logger.debug(error)
                    option_type = 'unknown'
                
                if error: # validation of option failed                    
                    self.log_error(error=self.constants.error_name,
                                   message=self.constants.bad_option_message.format(option=option,
                                                                                    section=section,
                                                                                    error=error,
                                                                                    option_type=option_type))
                else: # missing option
                    self.log_error(error=self.constants.error_name,
                                   message=self.constants.missing_option_message.format(option=option,
                                                                                   section=section,
                                                                                   option_type=option_type,
                                                                                   plugin=self.plugin_name))
            else: # section missing
                self.log_error(error=self.constants.error_name,
                               message=self.constants.missing_section_message.format(section=section,
                                                                                plugin=self.plugin_name))
        return not self.validation_outcome is True

    def check_extra_values(self, warn_user=True):
        """
        checks the configuration for values not in the configspec

        :return: True if extra values, false otherwise
        """
        if warn_user:
            logger = self.logger.warning
        else:
            # in case the plugin does not care
            logger = self.logger.debug
            
        extra_values = get_extra_values(self.configuration)

        for sections, name in extra_values:
            # sections is a tuple of all the sections and subsections
            # leading to the option so we have to get to the bottom
            bottom_section = self.configuration
            for section in sections:
                bottom_section = bottom_section[section]

            # value is the extra item (either a value or section)
            value = bottom_section[name]
            
            item_type = 'option'
            if isinstance(value, dict):
                item_type = 'section'
            
            section = ','.join(sections)
            if len(section):
                section = "{0},{1}".format(self.section_name, section)
            else:
                section = self.section_name
            message = self.constants.extra_message.format(section=section,
                                                          item_type=item_type,
                                                          name=name)
            if item_type == 'option':
                message += "='{0}'".format(value)
            logger(message)
                 
        return len(extra_values) > 0

    def check_rep(self):
        """
        Calls process_errors

        :raise: ConfigurationError if errors are found (or there are unknown options and not allow_extras)
        """
        extras_error = (not self.allow_extras) and (self.check_extra_values())

        try:
            if self.process_errors() or extras_error:
                self.logger.info('Expected Configuration Matching:\n{0}'.format(self.sample))
                raise ConfigurationError(self.constants.check_rep_failure_message.format(self.section_name))
        except KeyError as error:
            self.logger.debug(error)
            self.logger.info('Expected Configuration Matching:\n{0}'.format(self.sample))
            raise ConfigurationError(self.constants.check_rep_failure_message.format(self.section_name))
        return            
# end SubConfiguration        


class BaseConfiguration(SubConfiguration):
    """
    A BaseConfiguration to build the product and hold the configuration
    """
    def __init__(self, **kwargs):
        super(BaseConfiguration, self).__init__(**kwargs)
        self._product = None
        return
        
    @abstractproperty
    def product(self):
        """
        abstract: A built product to run
        """
# end class BaseConfiguration
