# -*- coding: utf-8 -*-
# Extract information from binary files

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from . import tika
import tempfile
import os

def get_content(binary_data, file_suffix=''):
    f = tempfile.NamedTemporaryFile(mode='w+b', 
            delete=False, suffix=file_suffix)
    path = f.name
    with f:
        f.write(binary_data)
    content = tika.get_content(path)
    os.unlink(path)
    return content


def get_metadata(binary_data, file_suffix=''):
    f = tempfile.NamedTemporaryFile(mode='w+b', 
            delete=False, suffix=file_suffix)
    path = f.name
    with f:
        f.write(binary_data)
    metadata = tika.get_metadata(path)
    os.unlink(path)
    return metadata

