# -*- coding: utf-8 -*-
import os
import types


def get_file_extension(filename):
    return os.path.splitext(filename)[1][1:].lower()


def has_file_extension(filename, extensions):
    if not isinstance(extensions, (types.ListType, types.TupleType)):
        extensions = (extensions,)
    fileext = get_file_extension(filename).lower()
    return fileext in [x.lower() for x in extensions]
