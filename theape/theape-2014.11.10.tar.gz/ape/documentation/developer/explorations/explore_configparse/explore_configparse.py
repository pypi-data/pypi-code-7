
# python standard library
from ConfigParser import SafeConfigParser
import ConfigParser
import glob
import os

# this package
from ape.commoncode.code_graphs import module_diagram


FILE_1 = 'config_1.ini'
FILE_2 = 'config_2.ini'
FILE_3 = 'config_3.ini'
FILE_4 = 'config_4.ini'
SAMPLE_BASE = 'sample_a.ini'


class FakeConfigParser(SafeConfigParser):
    pass


this_file = os.path.join(os.getcwd(), 'explore_configparse.py')
module_diagram_file = module_diagram(module=this_file, project='exploreconfigparse')
print ".. image:: {0}".format(module_diagram_file)


case_config = SafeConfigParser()
case_config.read(FILE_1)


print "Matches section camel-case: {0}".format(case_config.has_section('CamelCase'))
print "Matches section all-caps: {0}".format(case_config.has_section('CAMELCASE'))


print "Matches option camel-case: {0}".format(case_config.has_option('CamelCase', 'OptionOne'))
print "Matches option all-lower: {0}".format(case_config.has_option('CamelCase', 'optionone'))


case_config.optionxform = str
print "Matches option camel-case: {0}".format(case_config.has_option('CamelCase', 'OptionOne'))
print "Matches option all-lower: {0}".format(case_config.has_option('CamelCase', 'optionone'))


print case_config.options('CamelCase')


case_config.read(FILE_1)
print "Matches option camel-case: {0}".format(case_config.has_option('CamelCase', 'OptionOne'))
print "Matches option all-lower: {0}".format(case_config.has_option('CamelCase', 'optionone'))
print case_config.options('CamelCase')


case_config.remove_section('CamelCase')
case_config.read(FILE_1)
print "Matches option camel-case: {0}".format(case_config.has_option('CamelCase', 'OptionOne'))
print "Matches option all-lower: {0}".format(case_config.has_option('CamelCase', 'optionone'))
print case_config.options('CamelCase')


HEADER = """
.. csv-table:: {section}
   :header: Option,Value

"""

LINE = "   {option},{value}"

def print_config(parser):
    """
    Sends a rst csv-table to stdout

    :param:

     - `parser`: loaded ConfigParser
    """
    try:
        for section in sorted(parser.sections()):
            print HEADER.format(section=section)
            for option,value in parser.items(section):
                print LINE.format(option=option,
                                  value=value)
    except ConfigParser.Error as error:
        print error
    return


safe_config = SafeConfigParser()
safe_config.read((FILE_1, FILE_1))


print_config(safe_config)


safe_config.read(FILE_2)


print_config(safe_config)


config = SafeConfigParser()
config.read(FILE_3)


print_config(config)


config = SafeConfigParser()
config.read(FILE_4)


print_config(config)


config = SafeConfigParser()
names = []
names.extend(config.read(SAMPLE_BASE))
for name in glob.iglob(config.get('DEFAULT', 'glob')):
    names.extend(config.read(name))


print_config(config)


print "\nFilenames Read:"
for name in names:
    print "   {0}".format(name)
