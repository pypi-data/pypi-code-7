import os
import sys
import argparse

from .mutt import mutt
from .index import index
from .search import search
from .sort import sort

def parser():
    DIR = os.path.expanduser('~/.cbuh')
    epilog = '''
Search the contact list in ~/.cbuh/contacts. The search is an ordinary Xapian
query (http://xapian.org/docs/queryparser.html) with whatever prefixed terms
you like. I suggest these.

* id
* name
* email
* phone
* place

If you apply these prefixes, you search within that field only;
for example, "name:Francisco" searches for people with names like
"Francisco". Searching for simply "Francisco", on the other hand,
will also match everyone who lives in San Francisco.

Prefixes that start with digits 0 to 4 are treated as numeric values,
with the digit being the slot. For example, I use ``1want`` to
indicate how much I want to see someone, so I can search for people
I really want to see with ``want20..``.

Prefixes that start with digits 5 to 9 are treated as date values,
with the digit being the slot. For example, I use ``6born`` to indicate
when someone was born.
'''
    p = argparse.ArgumentParser(description = 'Query the contact list.',
        epilog = epilog, formatter_class = argparse.RawDescriptionHelpFormatter)

    # Import and export
    p.add_argument('-s', '--sort', action = 'store_true', default = False,
        help = 'Sort the contacts file by person identifier.')
    p.add_argument('-m', '--mutt', action = 'store_true', default = False,
        help = 'Export the contact list as a mutt alias file.')

    # Files
    p.add_argument('-c', '--contacts', metavar = 'path', action = 'store',
        default = os.path.join(DIR, 'contacts'), help = 'The contacts file')
    p.add_argument('-d', '--database', metavar = 'path', action = 'store',
        default = os.path.join(DIR, 'db'), help = 'The database directory')
    p.add_argument('-p', '--prefixes', metavar = 'path', action = 'store',
        default = os.path.join(DIR, 'prefixes'), help = 'The prefixes file')

    # Search
    p.add_argument('-i', '--index', action = 'store_true', default = False,
        help = 'Index the contact list.')
    p.add_argument('search', metavar = '[search term]', nargs = '*',
        help = 'The search terms, if you\'re running a search')
    return p


def cli():
    p = parser()
    a = p.parse_args()

    if a.sort:
        sort(a.contacts)

    if a.index:
        index(a.contacts, a.database, a.prefixes)

    if a.mutt:
        for alias in mutt(a.contacts):
            sys.stdout.write(alias + '\n')

    if len(a.search) > 0:
        for person in search(a.database, a.prefixes, ' AND '.join(a.search)):
            sys.stdout.write(person + '\n')

    if len(a.search) == 0 and (not a.mutt) and (not a.index) and (not a.sort):
        p.print_help()
        sys.exit(2)
