#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 mjirik <mjirik@mjirik-Latitude-E6520>
#
# Distributed under terms of the MIT license.

"""
Module is used to find library
"""

import logging
logger = logging.getLogger(__name__)
import argparse
import fnmatch
import os

import pickle


def find_file(start_dir="~", filemask="larcc.py"):
    start_dir = os.path.expanduser(start_dir)

    matches = []
    for root, dirnames, filenames in os.walk(start_dir):
        for filename in fnmatch.filter(filenames, filemask):
            matches.append(os.path.join(root, filename))
    return matches


def find_library_path(libname, referencelibfile):
    import_info_file = 'import_path_' + libname + '.p'
    try:
        library_path = pickle.load(open(import_info_file, "rb"))
#        sys.path.insert(0, import_path)
    except:
        matches = find_file(filemask=referencelibfile)
        library_path, filename = os.path.split(matches[0])
        data = library_path
        pickle.dump(data, open(import_info_file, "wb"))

    return library_path


def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        ch.setLevel(logging.DEBUG)

    print find_file()


if __name__ == "__main__":
    main()
