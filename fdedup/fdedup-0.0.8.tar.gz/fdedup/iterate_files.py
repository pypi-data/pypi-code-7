# -*- coding: utf-8 -*-

import logging
import os


logger = logging.getLogger(__package__)


def _iterate_files(path, onerror=None):
    if os.path.isfile(path):
        yield path

    for path, _, files in os.walk(path, onerror=onerror):
        for f in files:
            yield os.path.join(path, f)


def iterate_files(paths, onerror=None):
    """
    Iterate over all files in the provided paths

    Args:
        paths (list): list of paths to iterate
        onerror: onerror callback passed to os.walk

    Returns:
        iterator to all files
    """
    for path in paths:
        for f in _iterate_files(path, onerror=onerror):
            yield f
