# -*- coding: utf-8 -*-

import functools
import hashlib
import logging
import itertools
import os
import collections

from iterate_files import iterate_files


logger = logging.getLogger(__package__)


def chunk_reader(fileobject, chunk_size):
    while True:
        chunk = fileobject.read(chunk_size)
        if not chunk:
            break
        yield chunk


def file_size(path, empty_as_none=False):
    size = os.path.getsize(path)
    if empty_as_none:
        return size if size else None
    else:
        return size


def file_hash(path, algorithm='md5', size=-1, chunk_size=65536):
    try:
        hasher = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            read = 0
            for chunk in chunk_reader(f, chunk_size):
                read += len(chunk)
                hasher.update(chunk)
                if size != -1 and read >= size:
                    break
        return hasher.hexdigest()

    except IOError as e:
        logger.error(e)
        return None


def find_candidates(groups, func):
    candidates = collections.defaultdict(list)
    for group in groups:
        group_candidates = collections.defaultdict(list)
        for path in group:
            filehash = func(path)
            if filehash is not None:
                group_candidates[filehash].append(path)
        # TODO(malkolm) Figure out if this doubles memory usage when len(groups) == 1
        for filehash, paths in (item for item in group_candidates.iteritems() if len(item[1]) > 1):
            candidates[filehash].extend(paths)
    return (set(v) for v in candidates.itervalues() if len(v) > 1)


def verify_paths(paths):
    for path in paths:
        os.stat(path)


def find_duplicates(paths, algorithm='md5', verify=False, ignore_empty=False):
    verify_paths(paths)

    def onerror(err):
        if err.errno != 20:  # 'Not a directory'
            logger.error(err)

    hash_func = functools.partial(file_hash, algorithm=algorithm)

    paths = (os.path.normpath(path) for path in paths)
    paths = iterate_files(paths, onerror=onerror)
    groups = [paths]
    groups = find_candidates(groups, functools.partial(file_size, empty_as_none=ignore_empty))
    groups = find_candidates(groups, lambda path: hash_func(path, size=1024))
    groups = find_candidates(groups, hash_func)
    if verify:
        import filecmp

        def cmp_files(filepaths):
            return all(
                itertools.starmap(
                    lambda l, r: filecmp.cmp(l, r, shallow=False),
                    itertools.combinations(filepaths, 2)))

        groups_verified = []
        for group in groups:
            group = list(group)
            if cmp_files(group):
                groups_verified.append(group)
            else:
                logger.error('Hash collision detected: %s', ', '.join(sorted(group)))
        groups = groups_verified
    return groups