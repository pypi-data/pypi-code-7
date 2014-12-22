# -*- coding: utf-8 -*-
# Extract information from binary files

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from . import tika
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


def get_content(binary_data, filename=''):
    logger.info("Extracting content from binary (bytes=%s, filename='%s')",
        len(binary_data), filename)

    _, ext = os.path.splitext(filename)
    f = tempfile.NamedTemporaryFile(mode='w+b', 
            delete=False, suffix=ext)
    path = f.name
    with f:
        f.write(binary_data)
    content = tika.get_content(path)
    os.unlink(path)
    return unicode(content, errors='ignore')


def get_metadata(binary_data, filename=''):
    _, ext = os.path.splitext(filename)
    f = tempfile.NamedTemporaryFile(mode='w+b', 
            delete=False, suffix=ext)
    path = f.name
    with f:
        f.write(binary_data)
    metadata = tika.get_metadata(path)
    os.unlink(path)
    return metadata

