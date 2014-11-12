#!/usr/bin/env python

"""
dev -- execute the development command for the current working directory.

Usage:

  In a directory with a registered command:

    dev

  To register a new command:

    dev command with spaces

"""

import os
import sys
import cPickle

__version__ = '0.1.1'

database = None
config_file = os.path.expanduser('~/.devdb')

def main():
    global database

    # Load database...
    try:
        f = open(config_file)
    except IOError:
        database = {}
    else:
        database = cPickle.load(f)
        f.close()

    # Figure out the current directory.
    path = os.getcwd()

    if path not in database or len(sys.argv) > 1:
        register_command(path)

    command = database[path]
    print("\033[35m%(path)s: %(command)r \033[m" % locals())
    run(command)

def usage():
    sys.stderr.write(__doc__)

def register_command(path):
    command = sys.argv[1:]
    if not command:
        sys.stderr.write("No command registered for: %s\n" % path)
        usage()
        exit(-1)

    database[path] = ' '.join(command)

    with open(config_file, 'wb') as f:
        cPickle.dump(database, f)

    return database[path]

def run(command):
    os.execl('/bin/sh', 'sh', '-c', command)

if __name__ == '__main__':
    main()
