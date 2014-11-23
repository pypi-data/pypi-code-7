from ConfigParser import ConfigParser
import re

def config(fn):
    c = ConfigParser()
    c.read(fn)
    for section in c.sections():
        yield section, list(data(c.items(section)))

def data(items):
    for key, values in items:
        for value in re.split(r'; ?', values):
            yield key, value
