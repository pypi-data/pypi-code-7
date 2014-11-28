#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import hashlib
import logging
import sys

from fdedup.log_count_handler import LogCountHandler
from fdedup.find_duplicates import find_duplicates

logger = logging.getLogger(__package__)


def read_paths():
    """
    Read paths from sys.stdin ignoring empty lines.

    Returns:
        iterator to read paths
    """
    for path in sys.stdin:
        path = path.rstrip()  # drop \n
        if path:  # skip empty lines
            yield path


def main(args=None):
    """
    Args:
        args (array): args

    Returns:
        int: The return code.

        0 -- Success.
        1 -- No good.
        2 -- Invalid usage.
    """
    parser = argparse.ArgumentParser(
        description='Find file duplicates.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('paths', nargs='+', metavar='PATH', help='paths to scan for duplicates')

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='count', default=0, help='be verbose')
    verbosity.add_argument('-q', '--quiet', action='store_true', help='be quiet')

    parser.add_argument('--ignore-empty', action='store_true', help='ignore empty files')
    parser.add_argument('--algorithm', choices=hashlib.algorithms, default='md5', help='hash algorithm to use')
    parser.add_argument('--verify', action='store_true', help='verify duplicates bytewise')
    parser.add_argument('--json', action='store_true', help='report in json')
    opts = parser.parse_args(args)

    logger.level = logging.WARN
    log_format = '%(name)s: %(message)s'
    if opts.verbose == 1:
        logger.level = logging.INFO
    elif opts.verbose > 1:
        log_format = '[%(asctime)s %(levelname)s] %(name)s: %(message)s'
        logger.level = logging.DEBUG

    if opts.quiet:
        logger.disabled = True

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format, '%m/%d/%Y %H:%M:%S'))
    logger.addHandler(handler)

    log_counter = LogCountHandler()
    logger.addHandler(log_counter)

    if '-' in opts.paths:
        opts.paths.remove('-')
        opts.paths.extend(read_paths())

    try:
        groups = find_duplicates(opts.paths, verify=opts.verify, ignore_empty=opts.ignore_empty,
                                 algorithm=opts.algorithm)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    if opts.json:
        import json

        print json.dumps([list(group) for group in groups], indent=2)
    else:
        first = True
        for group in groups:
            if not first:
                print ''
            else:
                first = False
            for path in group:
                print path

    return log_counter.count(logging.ERROR) > 0
