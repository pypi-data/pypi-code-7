from collections import defaultdict
from .config import config
import ConfigParser

def sort(contacts):
    old = config(contacts)
    new = ConfigParser.ConfigParser()
    for section, olddata in sorted(old):
        new.add_section(section)
        newdata = defaultdict(list)
        for key, value in olddata:
            newdata[key].append(value)
        for key, values in sorted(newdata.items()):
            new.set(section, key, '; '.join(values))
    
    with open(contacts, 'w') as fp:
        new.write(fp)
