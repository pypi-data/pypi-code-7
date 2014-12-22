
# python standard library
import ConfigParser
import glob
import os
from collections import OrderedDict, namedtuple

# this package
from ape import BaseClass
from ape.infrastructure.code_graphs import module_diagram, class_diagram
from ape.infrastructure.errors import ConfigurationError
from ape.infrastructure.timemap import RelativeTime, AbsoluteTime


DEFAULT = 'DEFAULT'
CONFIG_GLOB = 'config_glob'
IN_PWEAVE = __name__ == '__builtin__'


class ConfigurationMap(BaseClass):
    """
    A map from configuration files to data
    """
    def __init__(self, filename):
        """
        ConfigurationMap constructor

        :param:

         - `filename`: filename(s) to create configuration
        """
        super(ConfigurationMap, self).__init__()
        self.filename = filename        
        self._parser = None
        return

    @property
    def parser(self):
        """
        A SafeConfigParser instance with `allow_no_value` set to True
        """
        if self._parser is None:
            self._parser = ConfigParser.SafeConfigParser(allow_no_value=True)
            self._parser.read(self.filename)
            if self._parser.has_option(DEFAULT, CONFIG_GLOB):
                for name in glob.iglob(self._parser.get(DEFAULT, CONFIG_GLOB)):
                    self._parser.read(name)
        return self._parser

    def get(self, section, option, optional=True, default=None):
        """
        Gets the option from the section as a string

        :param:

         - `section`: section within the config file
         - `option`: option within the section
         - `optional`: If true return default instead of raising error for missing option
         - `default`: what to return if optional and not found
        """
        try:
            return self.parser.get(section, option)
        except ConfigParser.NoOptionError as error:
            self.logger.debug(error)
        if optional:
            return default
        raise ConfigurationError('No Such Option -- section: {0} option: {1}'.format(section,
                                                                                     option))

    def get_type(self, cast, section, option, optional=False, default=None):
        """
        Gets a value and casts it

        :param:

         - `cast`: function to cast the value
         - `section`: section with value
         - `option`: option in section with value

        :return: value from section:option
        :raise: ConfigurationError if it can't be cast
        """
        try:
            return cast(self.get(section, option, optional, default))
        except ValueError as error:
            value = self.get(section,
                             option,
                             optional,
                             default)
            self.logger.error(error)

            output = 'Section: {0}, Option: {1}, Value: {2}'.format(section,
                                                                    option,
                                                                    value)
            self.logger.error(output)                                                                    
            raise ConfigurationError("cannot cast: {0} to {1}".format(value,
                                                                      cast))

        
    def get_int(self, section, option, optional=False, default=None):
        """
        gets the value as an integer

        :return: value from section:option
        :raise: ConfigurationError if it can't be cast
        """
        return self.get_type(int, section, option, optional, default)
        
    def get_float(self, section, option, optional=False, default=None):
        """
        gets the value as a float
        """
        return self.get_type(float, section, option, optional, default)

    def get_boolean(self, section, option, optional=False, default=None):
        """
        Gets a value and casts it to a boolean

        :param:

         - `cast`: function to cast the value
         - `section`: section with value
         - `option`: option in section with value

        :return: value from section:option
        :raise: ConfigurationError if it can't be cast
        """
        try:
            return self.parser.getboolean(section, option)
        except ConfigParser.NoOptionError as error:
            self.logger.debug(error)
            if optional:
                return default
            else:
                raise ConfigurationError('No Such Option -- section: {0} option: {1}'.format(section,
                                                                                             option))
        except ValueError as error:
            value = self.get(section,
                             option,
                             optional,
                             default)
            self.logger.error(error)

            output = 'Section: {0}, Option: {1}, Value: {2}'.format(section,
                                                                    option,
                                                                    value)
            self.logger.error(output)                                                                    
            raise ConfigurationError("cannot cast: {0} to boolean".format(value))

    # to make it look more like ConfigParser
    getint = get_int
    getfloat = get_float
    getboolean = get_boolean
    
    def get_list(self, section, option, optional=False, default=None, delimiter=','):
        """
        Gets the value and converts it to a list

        :return: value list with whitespace trimmed
        """
        values =  self.get(section, option, optional=False, default=None).split(delimiter)
        return [value.strip() for value in values]

    def get_tuple(self, section, option, optional=False, default=None, delimiter=','):
        """
        Gets the value and converts it to a list

        :return: value list with whitespace trimmed
        """
        return tuple(self.get_list(section, option, optional=False, default=None,
                                   delimiter=delimiter))

    def get_dictionary(self, section, option, optional=False, default=None,
                       delimiter=',', separator=':'):
        """
        converts a delimiter-separated line to a key:value based dictionary (values are strings)
        """
        line = self.get_list(section, option, optional=False, default=None,
                              delimiter=',')
        return dict(item.split(separator) for item in line)

    def get_ordered_dictionary(self, section, option, optional=False, default=None,
                               delimiter=',', separator=':'):
        """
        converts a delimiter-separated line to a key:value based dictionary (values are strings)
        """
        line = self.get_list(section, option, optional=False, default=None,
                              delimiter=',')
        return OrderedDict(item.split(separator) for item in line)

    def get_named_tuple(self, section, option, optional=False, default=None,
                               delimiter=',', separator=':', cast=str):
        """
        Converts a line to a named tuple (Like the get_dictionary but keys are properties)

        namedtuple(section, fields)

        :param:
        
         - `section`: section in config (used as name for namedtuple
         - `option`: with <field><delimiter><value><separator> <field><delimiter><value>
         - `optional`: if True, missing option returns default
         - `default`: if optional and no option, return this
         - `delimiter`: token to separate <field><value> pairs
         - `separator: token to separate each <field><value> pair
         - `cast`:  function to cast all values
        """
        line = self.get_list(section, option, optional=False, default=None,
                              delimiter=',')
        tokens = [token.split(separator) for token in line]
        fields = [token[0] for token in tokens]
        values = (cast(token[1]) for token in tokens)
        
        definition = namedtuple(section, fields)
        return definition(*values)

    def get_relativetime(self, section, option, optional=False, default=None):
        """
        Gets a relativetime object based on the option (assumes value is timestamp) (see timemap.RelativeTime)

        :return: RelativeTime object
        """
        source = self.get(section, option, optional, default)
        if source is not default:
            return RelativeTime(source=source)
        return default

    def get_datetime(self, section, option, optional=False, default=None):
        """
        Gets a datetime object based on the option (value is timestamp) (see timemap.AbsoluteTime)

        :return: datetime object or default
        """
        source = self.get(section, option, optional, default)
        if source is not default:
            abtime = AbsoluteTime()
            return abtime(source)
        return default
    

    @property
    def sections(self):
        """
        :return: section names other than DEFAULT
        """
        return self.parser.sections()

    def has_option(self, section, option):
        """
        :return: True if section has this option
        """
        return self.parser.has_option(section, option)

    def options(self, section, optional=False, default=None):
        """
        gets a list of option-names

        :param:

         - `section`: section-name in the configuration
        
        :return: options in section
        """
        try:
            return self.parser.options(section)
        except ConfigParser.NoSectionError as error:
            if optional:
                self.logger.debug(error)
                return DEFAULT
            raise
        return

    def items(self, section, optional=False, default=None):
        """
        Gets tuples of (option, value) pairs for section

        :return: tuples
        """
        try:
            return self.parser.items(section)
        except ConfigParser.NoSectionError as error:
            if optional:
                self.logger.debug(error)
                return default
            raise
        return

    @property
    def defaults(self):
        """
        the [DEFAULT] section

        :return: dict of default values        
        """
        return self.parser.defaults()

    def write(self, path):
        """
        Writes the current configuration to the path (filename)
        """
        with open(path, 'w') as f:
            self.parser.write(f)
        return
# end class ConfigurationMap    


if IN_PWEAVE:
    this_file = os.path.join(os.getcwd(), 'configurationmap.py')
    module_diagram_file = module_diagram(module=this_file, project='configurationmap')
    print ".. image:: {0}".format(module_diagram_file)
